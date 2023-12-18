import dateutil.parser

class NodeSeriePronoMetadata:
    def __init__(self,params):
        self.series_id = int(params["series_id"]) if "series_id" in params else None
        self.cal_id = int(params["cal_id"]) if "cal_id" in params else None
        self.cor_id = int(params["cor_id"]) if "cor_id" in params else None
        self.forecast_date = dateutil.parser.isoparse(params["forecast_date"]) if "forecast_date" in params else None
        self.qualifier = str(params["qualifier"]) if "qualifier" in params else None
    def to_dict(self):
        return {
            "series_id": self.series_id,
            "cal_id": self.cal_id,
            "cor_id": self.cor_id,
            "forecast_date": self.forecast_date,
            "qualifier": self.qualifier
        }
