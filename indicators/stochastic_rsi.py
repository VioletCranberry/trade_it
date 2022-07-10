from indicators.x_point import XPoint
from talib import STOCHRSI


class SRSI:
    def __init__(self,
                 data_frame,
                 column_name,
                 time_period,
                 fastk_period,
                 fastd_period,
                 fastd_matype,
                 limit_l,
                 limit_h):
        self.limit_l = limit_l
        self.limit_h = limit_h

        self.data = data_frame.copy()
        self.data["fastk"], self.data["fastd"] = STOCHRSI(
            self.data[column_name], timeperiod=time_period,
            fastk_period=fastk_period,
            fastd_period=fastd_period,
            fastd_matype=fastd_matype
        )

        cross_data = XPoint(self.data, "fastk", "fastd")
        # ["x"] crossing point of fastk and fastd lines
        self.data["x"] = cross_data.data["x"]
        # ["↑"] fastk is crossing fastd up   - buy condition
        self.data["↑"] = cross_data.data["↑"]
        # ["↓"] fastk is crossing fastd down - sell condition
        self.data["↓"] = cross_data.data["↓"]
        # ["↕"] direction of line after cross point
        self.data["↕"] = cross_data.data["↕"]

        # ["condition"] - current price condition
        self.data["condition"] = self.data.apply(
            lambda row: self.set_condition(row), axis=1
        )

    def set_condition(self, row):
        # if both fastk and fastd below low limit  -> oversold
        if (row["fastk"] < self.limit_l) | (row["fastd"] < self.limit_l):
            return "oversold"
        # if both fastk and fastd above high limit -> overbought
        if (row["fastk"] > self.limit_h) | (row["fastd"] > self.limit_h):
            return "overbought"
        # if both fastk and fastd within limits
        return "stale"
