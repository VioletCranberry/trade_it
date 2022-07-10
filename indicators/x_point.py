from indicators.helpers import set_trend_direction


class XPoint:
    def __init__(self, data_frame, col1_name, col2_name):
        self.data = data_frame.copy()
        self.col1_name = col1_name
        self.col2_name = col2_name

        # shift to previous columns row values
        col1_prev = self.data[self.col1_name].shift(1)
        col2_prev = self.data[self.col2_name].shift(1)

        # cross condition equals true when current col1 is bigger than current col2
        # and previous col1 is less or equal to previous col2 and vice versa
        cond1 = ((self.data[self.col1_name] > self.data[self.col2_name])
                 & (col1_prev <= col2_prev))
        cond2 = ((self.data[self.col1_name] < self.data[self.col2_name])
                 & (col1_prev >= col2_prev))

        # ["x"] crossing point of two columns
        self.data["x"] = (cond1 | cond2)
        # ["↑"] crossing point when col1 is crossing up col2
        self.data["↑"] = (self.data["x"] & cond1)
        # ["↓"] crossing point when col1 is crossing down col2
        self.data["↓"] = (self.data["x"] & cond2)
        # ["↕"] direction from first crossing point to the next
        self.data["↕"] = self.data.apply(
            lambda row: set_trend_direction(row), axis=1
        ).fillna(method="ffill")
