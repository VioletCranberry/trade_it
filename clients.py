from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from retry import retry
from helpers import id_generator
import pandas as pd
import logging
import socket
import sys


class BinanceClient:
    def __init__(self, api_key, api_secret, test_net=False, test_order=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.test_order = test_order

        self.client = self.init_binance_client()
        if test_net:
            self.client.API_URL = "https://testnet.binance.vision/api"
        logging.info(f"initialised Binance client [url] : {self.client.API_URL}")

        self.status = self.client.get_system_status()
        if self.status.get("status") == 0:
            logging.info("Binance is operating normally")
        if self.status.get("status") == 1:
            logging.fatal("Binance is under maintenance")
            sys.exit(1)

    @retry(socket.timeout, delay=5)
    def init_binance_client(self):
        return Client(self.api_key, self.api_secret)

    def get_binance_data(self, symbol, interval, start_time):
        logging.info(f"fetching data for {symbol}"
                     f" with interval {interval} "
                     f"for {start_time}")
        data = self.client.get_historical_klines(
            symbol, interval, start_time)
        return self.convert_binance_to_df(data)

    # calculate amount to buy based on asset's last price
    def get_trade_amount(self, symbol_pair, asset):
        price_l = self.client.get_symbol_ticker(
            symbol=symbol_pair).get("price")
        balance = self.client.get_asset_balance(
            asset)
        balance_price = balance.get('free')

        amount = float(balance_price) / float(price_l)

        logging.info(f"[{symbol_pair}] "
                     f"available for trade: [{amount}] "
                     f"based on [{price_l}] price / "
                     f"{balance_price} balance")

        return amount

    def get_order_status(self, symbol_pair, client_order_id):
        logging.info(f"getting status for [{client_order_id}]")
        order = self.client.get_order(
            symbol=symbol_pair,
            origClientOrderId=client_order_id
        )
        order_status = order.get("status")
        logging.info(f"order {client_order_id} status is {order_status}")
        return order_status

    def set_order(self, symbol_pair, side, _type, quantity):
        order_id = id_generator(22)

        logging.info(f"placing [{side}] order of type [{_type}] with id {order_id}")
        try:
            if not self.test_order:
                order = self.client.create_order(
                    symbol=symbol_pair, side=side,
                    type=_type, quantity=quantity,
                    newClientOrderId=order_id
                )
                return order
            else:
                logging.warning("this order is TEST order")
                order = self.client.create_test_order(
                    symbol=symbol_pair, side=side,
                    type=_type, quantity=quantity,
                    newClientOrderId=order_id
                )
                return order

        except BinanceOrderException as e:
            logging.warning(f"unable to place order: {e}")
            raise
        except BinanceAPIException as e:
            logging.warning(f"unable to place order: {e}")
            raise

    @staticmethod
    def convert_binance_to_df(data):
        logging.info("converting received orders to pandas df")
        df = pd.DataFrame(
            data,
            columns=['open_time', 'open', 'high', 'low',
                     'close', 'volume', 'close_time',
                     'qav', 'num_trades', 'taker_base_vol',
                     'taker_quote_vol', 'ignore'])
        df.index = pd.to_datetime(
            df['open_time'], unit='ms')
        return df
