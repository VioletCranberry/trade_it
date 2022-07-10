from indicators.helpers import set_trend_direction
from talib import DEMA as TA_DEMA


# Double Exponential Moving Average
class DEMA:
    def __init__(self, data_frame, column_name, time_period=9):
        self.data = data_frame.copy()
        self.data["dema"] = TA_DEMA(self.data[column_name],
                                    timeperiod=time_period)

        prev = self.data["dema"].shift(1)
        self.data["↑"] = (self.data["dema"] > prev)
        self.data["↓"] = (self.data["dema"] < prev)

        self.data["↕"] = self.data.apply(
            lambda row: set_trend_direction(row), axis=1
        ).fillna(method="ffill")

