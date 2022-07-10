from talib import RSI as TA_RSI


class RSI:
    def __init__(self, data_frame,
                 column_name,
                 time_period,
                 limit_l,
                 limit_h):
        self.limit_l = limit_l
        self.limit_h = limit_h

        self.data = data_frame.copy()
        self.data["RSI"] = TA_RSI(
            self.data[column_name], timeperiod=time_period)
        # ["condition"] - current price condition
        self.data["condition"] = self.data.apply(
            lambda row: self.set_condition(row), axis=1
        )

    def set_condition(self, row):
        # if rsi is below low limit  -> oversold
        if row["RSI"] < self.limit_l:
            return "oversold"
        # if rsi is above high limit -> overbought
        if row["RSI"] > self.limit_h:
            return "overbought"
        return "stale"
