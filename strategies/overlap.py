from indicators import RSI, SRSI, DEMA, XPoint
import logging


class RsiSrsiCross:
    def __init__(self, data_frame, column_name,
                 rsi_time_period, rsi_limit_l, rsi_limit_h,
                 srsi_time_period, srsi_fastk_period,
                 srsi_fastd_period, srsi_fastd_matype,
                 srsi_limit_l, srsi_limit_h):
        logging.info(f"applying strategy {__class__.__name__}")
        self.data = data_frame.copy()

        self.rsi = RSI(data_frame=self.data,
                       column_name=column_name,
                       time_period=rsi_time_period,
                       limit_l=rsi_limit_l,
                       limit_h=rsi_limit_h)

        self.srsi = SRSI(data_frame=self.data,
                         column_name=column_name,
                         time_period=srsi_time_period,
                         fastk_period=srsi_fastk_period,
                         fastd_period=srsi_fastd_period,
                         fastd_matype=srsi_fastd_matype,
                         limit_l=srsi_limit_l,
                         limit_h=srsi_limit_h)

        # ["rsi_condition"]  - current RSI  price condition
        self.data["rsi_condition"] = self.rsi.data["condition"]
        # ["srsi_condition"] - current SRSI price condition
        self.data["srsi_condition"] = self.srsi.data["condition"]

        # ["x"] crossing point of fastk and fastd lines
        self.data["x"] = self.srsi.data["x"]
        # ["↑"] fastk is crossing fastd up   - buy condition
        self.data["↑"] = self.srsi.data["↑"]
        # ["↓"] fastk is crossing fastd down - sell condition
        self.data["↓"] = self.srsi.data["↓"]
        # ["↕"] direction of line after cross point
        self.data["↕"] = self.srsi.data["↕"]

        # ["srsi_action"] - current recommended SRSI trade action
        self.data["srsi_action"] = self.data.apply(
            lambda row: self.set_action(row), axis=1
        )
        # ["action"] - current recommended trade action based on orders above
        self.data["action"] = self.data.apply(
            lambda row: self.action(row), axis=1
        )

    @staticmethod
    def set_action(row):
        # if there is a crossing point
        if row["x"]:
            # if price condition is oversold and fastk is crossing fastd up
            if row["srsi_condition"] == "oversold" and row["↕"] == "up":
                return "buy"
            # if price condition is overbought and fastk is crossing fastd down
            if row["srsi_condition"] == "overbought" and row["↕"] == "down":
                return "sell"
            # if none of it we should remain from trading
        return "hold"

    @staticmethod
    def action(row):
        # if RSI is in oversold condition
        if row["rsi_condition"] == "oversold":
            # if SRSI is in oversold condition
            if row["srsi_condition"] == "oversold":
                # if SRSI trade action is buy
                if row["srsi_action"] == "buy":
                    return "buy"
        # if RSI is in overbought condition
        if row["rsi_condition"] == "overbought":
            # if SRSI is in overbought condition
            if row["srsi_condition"] == "overbought":
                # if SRSI trade action is sell
                if row["srsi_action"] == "sell":
                    return "sell"
        # hold if none of the conditions were met
        return "hold"


class DoubleDemaCross:
    def __init__(self, data_frame, column_name,
                 dema_period_long, dema_period_short):
        logging.info(f"applying strategy {__class__.__name__}")
        self.data = data_frame.copy()

        self.data["dema_long"] = DEMA(
            data_frame=self.data,
            column_name=column_name,
            time_period=dema_period_long
        ).data["dema"]

        self.data["dema_short"] = DEMA(
            data_frame=self.data,
            column_name=column_name,
            time_period=dema_period_short
        ).data["dema"]

        cross_data = XPoint(self.data, "dema_short", "dema_long")
        # ["x"] crossing point of short and long lines
        self.data["x"] = cross_data.data["x"]
        # ["↑"] short is crossing long up  - buy condition
        self.data["↑"] = cross_data.data["↑"]
        # ["↓"] show is crossing long down - sell condition
        self.data["↓"] = cross_data.data["↓"]
        # ["↕"] direction of line after cross point
        self.data["↕"] = cross_data.data["↕"]

        # ["dema_action"] - current recommended SRSI trade action
        self.data["action"] = self.data.apply(
            lambda row: self.set_action(row), axis=1
        )

    @staticmethod
    def set_action(row):
        # if there is a crossing point
        if row["x"]:
            # if short is crossing long up
            if row["↕"] == "up":
                return "buy"
            # if short is crossing short down
            if row["↕"] == "down":
                return "sell"
            # if none of it we should remain from trading
        return "hold"
