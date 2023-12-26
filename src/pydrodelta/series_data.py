from pandas import DataFrame

class SeriesData(DataFrame):
    def __init__(self, *args, **kwargs):
        super(SeriesData, self).__init__(*args, **kwargs)
