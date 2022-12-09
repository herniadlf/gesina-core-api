import csv
import io
import re as regex
from src.persistance.scheduled_task import (
    BorderCondition,
    BorderConditionType,
)
from src.service.exception.file_exception import FileUploadError
from src.service.exception.series_exception import SeriesUploadError

SERIES_INTERVAL_REGEX = "^[0-9]*-(MINUTE|HOUR|DAY|WEEK)$"
NATIVE_SERIES_INTERVAL_REGEX = r"^([0-9]*)(MINUTE|HOUR|DAY|WEEK)$"

CSV_HEADERS = [
    "river",
    "reach",
    "river_stat",
    "interval",
    "type",
    "series_id",
]


def retrieve_series(form, scheduled_config_id=None):
    from_csv = process_series_file(form.series_list_file, scheduled_config_id)
    from_form = process_series_form(form.series_list, scheduled_config_id)
    merged_series = from_csv + from_form
    series_id_to_validate = []
    for series in merged_series:
        if not bool(regex.match(SERIES_INTERVAL_REGEX, series.interval)):
            raise SeriesUploadError("Error: Interval con formato incorrecto")
        series_id_to_validate.append(series.series_id)
    if len(series_id_to_validate) != len(set(series_id_to_validate)):
        raise SeriesUploadError("Error: No puede repetirse un Id de serie")

    return merged_series


def update_series_list(session, scheduled_config_id, series):
    session.query(BorderCondition).filter_by(
        scheduled_task_id=scheduled_config_id
    ).delete()
    for each_series in series:
        session.add(each_series)


def process_series_form(series_list, scheduled_config_id=None):
    result = []
    for each_series in series_list:
        interval_data = each_series.interval.data
        interval = (
            str(interval_data["interval_value"]) + "-" + interval_data["interval_unit"]
        )
        if scheduled_config_id:
            border_condition = BorderCondition(
                scheduled_task_id=scheduled_config_id,
                river=each_series.river.data,
                reach=each_series.reach.data,
                river_stat=each_series.river_stat.data,
                interval=interval,
                type=BorderConditionType(each_series.border_condition.data),
                series_id=each_series.series_id.data,
            )
        else:
            border_condition = BorderCondition(
                river=each_series.river.data,
                reach=each_series.reach.data,
                river_stat=each_series.river_stat.data,
                interval=interval,
                type=BorderConditionType(each_series.border_condition.data),
                series_id=each_series.series_id.data,
            )
        result.append(border_condition)

    return result


def process_series_file(series_file_field, scheduled_config_id=None):
    result = []
    if series_file_field.data:
        buffer = series_file_field.data.read()
        content = buffer.decode()
        file = io.StringIO(content)
        if ".csv" in series_file_field.data.filename:
            csv_data = csv.reader(file, delimiter=",")
            header = next(csv_data)
            if header == CSV_HEADERS:
                for row in csv_data:
                    if scheduled_config_id:
                        border_condition = BorderCondition(
                            scheduled_task_id=scheduled_config_id,
                            river=row[0],
                            reach=row[1],
                            river_stat=row[2],
                            interval=row[3],
                            type=row[4],
                            series_id=row[5],
                        )
                    else:
                        border_condition = BorderCondition(
                            river=row[0],
                            reach=row[1],
                            river_stat=row[2],
                            interval=row[3],
                            type=row[4],
                            series_id=row[5],
                        )
                    result.append(border_condition)
            else:
                raise FileUploadError("Error: Archivo .csv inválido")
        elif ".u" in series_file_field.data.filename:
            for line in file.readlines():
                line = line.rstrip()
                if line.startswith("DSS Path=") or (
                    line.startswith("Boundary Location=") and "river" in locals()
                ):
                    if scheduled_config_id:
                        border_condition = BorderCondition(
                            scheduled_task_id=scheduled_config_id,
                            river=river,
                            reach=reach,
                            river_stat=river_stat,
                            interval=interval,
                            type=t,
                        )
                    else:
                        border_condition = BorderCondition(
                            river=river,
                            reach=reach,
                            river_stat=river_stat,
                            interval=interval,
                            type=t,
                        )

                    del river, reach, river_stat, interval, t

                    result.append(border_condition)

                if line.startswith("Boundary Location="):
                    line_c = line.split("=")[1].split(",")
                    river, reach, river_stat = (
                        line_c[0].strip(),
                        line_c[1].strip(),
                        line_c[2].strip(),
                    )
                elif line.startswith("Interval="):
                    interval = line.split("=")[1].strip()
                    r = regex.search(NATIVE_SERIES_INTERVAL_REGEX, interval)
                    interval = f"{r.group(1)}-{r.group(2)}"
                elif line.startswith("Stage Hydrograph="):
                    t = line.split("=")[0].strip()
                elif line.startswith("Flow Hydrograph="):
                    t = line.split("=")[0].strip()
                elif line.startswith("Lateral Inflow Hydrograph="):
                    t = line.split("=")[0].strip()

    return result
