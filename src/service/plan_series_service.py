import csv
import io
from src.persistance.scheduled_task import PlanSeries
from src.service.exception.file_exception import FileUploadError
from src.service.exception.series_exception import SeriesUploadError

CSV_HEADERS = ["river", "reach", "river_stat", "stage_series_id", "flow_series_id"]


def retrieve_plan_series(form, scheduled_config_id=None):
    from_csv = process_plan_series_csv_file(form.plan_series_file, scheduled_config_id)
    from_form = process_plan_series_form(form.plan_series_list, scheduled_config_id)
    merged_series = from_csv + from_form
    stage_series_to_validate = [series.stage_series_id for series in merged_series]
    stage_series_as_set = set(stage_series_to_validate)
    flow_series_to_validate = [series.flow_series_id for series in merged_series]
    flow_series_as_set = set(flow_series_to_validate)
    if len(stage_series_to_validate) != len(stage_series_as_set):
        raise SeriesUploadError("Error: No puede repetirse un Id de serie de altura")
    if len(flow_series_to_validate) != len(flow_series_as_set):
        raise SeriesUploadError("Error: No puede repetirse un Id de serie de flujo")
    if len(stage_series_as_set.intersection(flow_series_as_set)) > 0:
        raise SeriesUploadError(
            "Error: No puede repetirse un Id entre series de flujo y series de altura"
        )

    return merged_series


def update_plan_series_list(session, scheduled_config_id, plan_series_list):
    session.query(PlanSeries).filter_by(scheduled_task_id=scheduled_config_id).delete()
    for plan_series in plan_series_list:
        session.add(plan_series)


def process_plan_series_form(series_list, scheduled_config_id=None):
    result = []
    for each_plan_series in series_list:
        if scheduled_config_id:
            plan_series = PlanSeries(
                scheduled_task_id=scheduled_config_id,
                river=each_plan_series.river.data,
                reach=each_plan_series.reach.data,
                river_stat=each_plan_series.river_stat.data,
                stage_series_id=each_plan_series.stage_series_id.data,
                flow_series_id=each_plan_series.flow_series_id.data,
            )
        else:
            plan_series = PlanSeries(
                river=each_plan_series.river.data,
                reach=each_plan_series.reach.data,
                river_stat=each_plan_series.river_stat.data,
                stage_series_id=each_plan_series.stage_series_id.data,
                flow_series_id=each_plan_series.flow_series_id.data,
            )
        result.append(plan_series)

    return result


def process_plan_series_csv_file(plan_series_file_field, scheduled_config_id=None):
    result = []
    if plan_series_file_field.data:
        buffer = plan_series_file_field.data.read()
        content = buffer.decode()
        file = io.StringIO(content)
        if ".csv" in plan_series_file_field.data.filename:
            csv_data = csv.reader(file, delimiter=",")
            header = next(csv_data)
            if header == CSV_HEADERS:
                for row in csv_data:
                    if scheduled_config_id:
                        plan_series = PlanSeries(
                            scheduled_task_id=scheduled_config_id,
                            river=row[0],
                            reach=row[1],
                            river_stat=row[2],
                            stage_series_id=row[3],
                            flow_series_id=row[4],
                        )
                    else:
                        plan_series = PlanSeries(
                            river=row[0],
                            reach=row[1],
                            river_stat=row[2],
                            stage_series_id=row[3],
                            flow_series_id=row[4],
                        )
                    result.append(plan_series)
            else:
                raise FileUploadError("Error: Archivo .csv inválido")
        elif ".p" in plan_series_file_field.data.filename:
            for line in file.readlines():
                line = line.rstrip()
                if line.startswith("Stage Flow Hydrograph="):
                    line = line.split("=")[1]
                    line = line.split(",")
                    river, reach, river_stat = (
                        line[0].strip(),
                        line[1].strip(),
                        line[2].strip(),
                    )
                    if scheduled_config_id:
                        plan_series = PlanSeries(
                            scheduled_task_id=scheduled_config_id,
                            river=river,
                            reach=reach,
                            river_stat=river_stat,
                        )
                    else:
                        plan_series = PlanSeries(
                            river=river, reach=reach, river_stat=river_stat
                        )
                    result.append(plan_series)

    return result
