from helpers import convert_row_timestamp, last_row_to_dict
from helpers import dict_to_json, last_order, clean_up_order
import logging


class TradeByLastRow:
    def __init__(self, data_frame, column_name, symbol_pair, tmp_file_name):
        self.symbol_pair = symbol_pair
        self.order_tmp_file = f"{tmp_file_name}/{self.symbol_pair}"

        logging.info(f"applying trade method {__class__.__name__}")
        self.data = data_frame.copy()
        self.dict = last_row_to_dict(
            self.data
        )
        logging.info(f"checking timeframe"
                     f" {convert_row_timestamp(self.dict.get('open_time'))}/"
                     f"{convert_row_timestamp(self.dict.get('close_time'))}")

        self.trade_action = self.dict.get(column_name)
        self.trade_signal = self.trade(
            self.trade_action)

    def trade(self, action):
        logging.info(f"evaluating action [{self.trade_action}]")

        previous_order = last_order(self.order_tmp_file)

        if self.trade_action not in ["buy", "sell", "hold"]:
            logging.warning(f"invalid action {action} found!")

        if self.trade_action == "buy":
            if not previous_order:
                dict_to_json(self.dict, self.order_tmp_file)
                return "buy"
            else:
                return "hold"

        if self.trade_action == "sell":
            if previous_order:
                clean_up_order(previous_order)
                return "sell"
            else:
                return "hold"

        if self.trade_action == "hold":
            return self.trade_action
