# Table of Contents

* [pydrodelta.types.plot\_params\_dict](#pydrodelta.types.plot_params_dict)
  * [PlotParamsDict](#pydrodelta.types.plot_params_dict.PlotParamsDict)

<a id="pydrodelta.types.plot_params_dict"></a>

# pydrodelta.types.plot\_params\_dict

<a id="pydrodelta.types.plot_params_dict.PlotParamsDict"></a>

## PlotParamsDict Objects

```python
class PlotParamsDict(TypedDict)
```

figsize : List[float]
           x y size of the plot in cm,
           default: [
               14,
               12
           ]
       forecast_date_annotation : str
           Annotation for forecast date,
           default: forecast date
       errorBandLabel : str
           Legend label for error band,
           default: error band
       prono_annotation : str
           Annotation for forecast period,
           default: forecast
       obs_annotation : str
           Annotation for observed period,
           default: past
       x_label : str
           Label for time axis,
           default: date
       y_label : str
           Label for values axis,
           default: value
       datum_template_string : str
           Template string for datum text. Use '%s' to interpolate datum value,
           examples: [
               Observed precipitation at %s
           ]
       title_template_string : str 
           Figure title template string. Use '%s' to interpolate station_name,
           default: forecast at %s
       obs_label : str
           Legend label for observed data,
           default: observed
       prono_label : str
           Legend label for forecast data,
           default: forecasted
       footnote : str
           Footnote text,
           examples: [
               This is the footnote text.
           ]
       xlim : List[datetime]
           bounds of the x axis (dates or intervals),
       ylim: List[float]
           bounds of the y axis,
           default: [
               0,
               2.5
           ]
       station_name : str
           Station name. Overrides node station metadata,
           default: Station
       output_file : str
           plot output file location,
       ydisplay : float
           y coordinate of the annotations,
           default: 1
       text_xoffset : List[float]
           x offset in points from default position of the annotations. First is for observations, second for forecast,
           default: [
               -8,
               -8
           ]
       xytext : List[float[
           not used,
           default: [
               -300,-200
           ]
       prono_fmt: str
           Style for forecast series,
           default: b-
       annotate: bool
           Add observed data/forecast data/forecast date annotations,
           default: True
       table_columns : List[str]
           Which forecast dataframe columns to show,
           items: {
               type: string, 
               enum: [
               Fecha,
               Nivel,
               Hora,
               Fechap,
               Dia,
               dd/mm hh
               ]
           },
           default: [
               Fecha,
               Nivel
           ]
       date_form : str
           Date formatting string for x axis tick labels,
           default: %H hrs 
%d-%b
       xaxis_minor_tick_hours : List[int]
           Hours of location of minor ticks of x axis,
           default: [3,9,15,21]
       errorBand : Tuple[str,str]
           Columns to use as error band (lower bound, upper bound). If not set and series_prono.adjust_results is True, 'error_band_01' and 'error_band_99' resulting from the adjustment are used,
       error_band_fmt : Union[str, Tuple[str,str]
           Style for error band,
           default: k-
       forecast_table : bool
           Print forecast table,
           default: true
       footnote_height : float
           Height of space for footnote in inches,
           default: 0.2
       prono_annotation_color : str
           forecast annotation color,
           default: black
       format : str
           output image file format,
           default: png

