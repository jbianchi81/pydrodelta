from pydrodelta.derived_origin import DerivedOrigin
from pydrodelta.interpolated_origin import InterpolatedOrigin
import logging
from datetime import timedelta
from pydrodelta.a5 import createEmptyObsDataFrame
from pydrodelta.util import applyTimeOffsetToIndex

class DerivedNodeSerie:
    def __init__(self,params,topology):
        self.series_id = params["series_id"] if params["series_id"] else None
        if "derived_from" in params:
            self.derived_from = DerivedOrigin(params["derived_from"],topology)
        else:
            self.derived_from = None
        if "interpolated_from" in params:
            self.interpolated_from = InterpolatedOrigin(params["interpolated_from"],topology)
        else:
            self.interpolated_from = None
        self.data = None
    def deriveTag(self,row,tag_column,tag="derived"):
        if row[tag_column] is None:
            return tag
        else:
            return "%s,%s" % (row[tag_column], tag)
    def deriveOffsetIndex(self,row,x_offset):
        return row.name + x_offset
    def derive(self,keep_index=True):
        if self.derived_from is not None:
            logging.debug("Deriving %i from %s" % (self.series_id, self.derived_from.origin.name))
            if not len(self.derived_from.origin.data):
                logging.warn("No data found to derive from origin. Skipping derived node")
                self.data = createEmptyObsDataFrame()
                return
            self.data = self.derived_from.origin.data[["valor","tag"]] # self.derived_from.origin.series[0].data[["valor",]]
            if isinstance(self.derived_from.x_offset,timedelta):
                self.data["valor"] = self.data["valor"] + self.derived_from.y_offset
                self.data.index = self.data.apply(lambda row: self.deriveOffsetIndex(row,self.derived_from.x_offset),axis=1)# for x in self.data.index]
                self.data["tag"] = self.data.apply(lambda row: self.deriveTag(row,"tag"),axis=1) # ["derived" if x is None else "%s,derived" % x for x in self.data.tag]
            else:
                self.data["valor"] = self.data["valor"].shift(self.derived_from.x_offset, axis = 0) + self.derived_from.y_offset
            self.data["tag"] = self.data.apply(lambda row: self.deriveTag(row,"tag"),axis=1) #["derived" if x is None else "%s,derived" % x for x in self.data.tag]
            if hasattr(self.derived_from.origin,"max_obs_date"):
                self.max_obs_date = self.derived_from.origin.max_obs_date
        elif self.interpolated_from is not None:
            logging.debug("Interpolating %i from %s and %s" % (self.series_id, self.interpolated_from.origin_1.name, self.interpolated_from.origin_2.name))
            if not len(self.interpolated_from.origin_1.data) or not len(self.interpolated_from.origin_2.data):
                logging.warn("No data found to derive from origin. Skipping derived node")
                self.data = createEmptyObsDataFrame()
                return
            self.data = self.interpolated_from.origin_1.data[["valor","tag"]] # self.interpolated_from.origin_1.series[0].data[["valor",]]
            self.data = self.data.join(self.interpolated_from.origin_2.data[["valor","tag"]],how='left',rsuffix="_other") # self.data.join(self.interpolated_from.origin_2.series[0].data[["valor",]],how='left',rsuffix="_other")
            self.data["valor"] = self.data["valor"] * (1 - self.interpolated_from.interpolation_coefficient) + self.data["valor_other"] * self.interpolated_from.interpolation_coefficient
            self.data["tag"] = self.data.apply(lambda row: self.deriveTag(row,"tag","interpolated"),axis=1) #["interpolated" if x is None else "%s,interpolated" % x for x in self.data.tag]
            del self.data["valor_other"]
            del self.data["tag_other"]
            if isinstance(self.interpolated_from.x_offset,timedelta):
                if keep_index:
                    self.data = applyTimeOffsetToIndex(self.data,self.interpolated_from.x_offset)
                else:
                    self.data.index = self.data.apply(lambda row: self.deriveOffsetIndex(row,self.interpolated_from.x_offset),axis=1) # for x in self.data.index]
            else:
                self.data[["valor","tag"]] = self.data[["valor","tag"]].shift(self.interpolated_from.x_offset, axis = 0)    
            if hasattr(self.interpolated_from.origin_1,"max_obs_date"):
                self.max_obs_date = self.interpolated_from.origin_1.max_obs_date
            
    def toCSV(self,include_series_id=False):
        if include_series_id:
            data = self.data
            data["series_id"] = self.series_id
            return data.to_csv()
        return self.data.to_csv()
    def toList(self,include_series_id=False,timeSupport=None):
        data = self.data
        data["timestart"] = data.index
        data["timeend"] = [x + timeSupport for x in data["timestart"]] if timeSupport is not None else data["timestart"]
        data["timestart"] = [x.isoformat() for x in data["timestart"]]
        data["timeend"] = [x.isoformat() for x in data["timeend"]]
        if include_series_id:
            data["series_id"] = self.series_id
        return data.to_dict(orient="records")
