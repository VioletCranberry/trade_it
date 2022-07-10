from binance.exceptions import BinanceOrderException, BinanceAPIException
from helpers import clean_up_order
import logging
import importlib
import sys
import asyncio


def validate_cls(package, class_name):
    try:
        module = importlib.import_module(package)
        _class = getattr(module, class_name)
        return _class
    except ModuleNotFoundError as err:
        logging.fatal(f"module {package} is incorrect: {err}")
        sys.exit(1)
    except AttributeError:
        logging.fatal(f"there is no class {class_name}"
                      f" for {package}")


async def process_data_to_trade(data, client):
    logging.info("processing market data")

    frame_settings = data.get("settings")
    trade_settings = data.get("trade")

    symbol_pair = frame_settings.get("symbols")

    # instantiate trade strategy
    strategy = validate_cls(
        "strategies",
        trade_settings.get("strategy")
    )

    # instantiate trade method
    method = validate_cls(
        "trade_methods",
        trade_settings.get("method")
    )

    client.get_trade_amount(symbol_pair,
                            frame_settings.get(
                                "base_asset"))

    # get binance market data
    market_data = client.get_binance_data(
        symbol_pair,
        frame_settings.get("for_each"),
        frame_settings.get("duration"))

    # enhance market data with strategy
    enhanced_market_data = strategy(
        market_data, "close",
        **trade_settings.get("params"))

    # evaluate and set last trading signal
    trade_signal = method(
        enhanced_market_data.data,
        "action",
        symbol_pair,
        data.get("order_tmp_folder")
    )

    return trade_signal


async def process_trade_signal(data, client, trade_signal):

    frame_settings = data.get("settings")

    if trade_signal.trade_signal == "buy":
        try:
            order = client.set_order(
                trade_signal.symbol_pair,
                "BUY", "MARKET",
                frame_settings.get("trade_quantity"))
            client.get_order_status(
                trade_signal.symbol_pair,
                order.get("clientOrderId")
            )
        except BinanceOrderException as e:
            logging.warning(f"Binance exception: {e}")
            clean_up_order(trade_signal.order_tmp_file)
        except BinanceAPIException as e:
            logging.warning(f"Binance exception: {e}")
            clean_up_order(trade_signal.order_tmp_file)

    if trade_signal.trade_signal == "sell":
        order = client.set_order(
            trade_signal.symbol_pair,
            "SELL", "MARKET",
            frame_settings.get("trade_quantity"))
        client.get_order_status(
            trade_signal.symbol_pair,
            order.get("clientOrderId")
        )


async def process_all(client, data):
    trade_signal = await process_data_to_trade(data, client)
    await process_trade_signal(data, client, trade_signal)

    sleep_time = data.get("async").get("sleep_seconds")
    logging.info(f"sleeping for "
                 f"{sleep_time} seconds")
    # sleep(sleep_time)
    await asyncio.sleep(sleep_time)
