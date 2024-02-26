from flask_wtf.file import FileField
from sqlalchemy import func

from src.persistance import User
from src.persistance.scheduled_task import ScheduledTask
from src.persistance.session import get_session
from src.service import project_file_service, plan_file_service, file_storage_service
from src.service.file_storage_service import save_restart_file
from src.service.user_service import get_current_user
from src.service.initial_flow_service import *
from src.service.border_series_service import *
from src.service.plan_series_service import *


def create(params, start_condition_type, restart_file_data, project_file_data, plan_file_data):
    with get_session() as session:
        scheduled_task = ScheduledTask(**params)
        session.add(scheduled_task)

        session.commit()
        session.refresh(scheduled_task)
        if start_condition_type == "restart_file":
            save_restart_file(restart_file_data, scheduled_task.id)

        project_file_service.process_project_template(
            project_file_data, scheduled_task.id
        )
        plan_file_service.process_plan_template(plan_file_data, scheduled_task.id)

        return scheduled_task


def update(_id, form):
    with get_session() as session:
        schedule_config = session.query(ScheduledTask).filter_by(id=_id).one_or_none()
        schedule_config.frequency = form.frequency.data
        schedule_config.calibration_id = form.calibration_id.data
        schedule_config.calibration_id_for_simulations = (
            form.calibration_id_for_simulations.data
        )
        schedule_config.name = form.name.data
        schedule_config.description = form.description.data
        schedule_config.geometry_id = form.geometry_id.data
        schedule_config.start_datetime = form.start_datetime.data
        schedule_config.enabled = form.enabled.data
        schedule_config.observation_days = form.observation_days.data
        schedule_config.forecast_days = form.forecast_days.data
        schedule_config.start_condition_type = form.start_condition_type.data
        update_series_list(session, _id, retrieve_series(form, _id))
        update_plan_series_list(session, _id, retrieve_plan_series(form, _id))

        if form.start_condition_type.data == "restart_file" and form.restart_file.data:
            save_restart_file(form.restart_file.data, schedule_config.id)
        else:
            update_initial_flows(session, _id, retrieve_initial_flows_from_form(form, _id))

        project_file_service.process_project_template(form.project_file.data, _id)
        plan_file_service.process_plan_template(form.plan_file.data, _id)
        session.add(schedule_config)


def create_from_form(form):
    params = {
        "frequency": form.frequency.data,
        "calibration_id": form.calibration_id.data,
        "calibration_id_for_simulations": form.calibration_id_for_simulations.data,
        "enabled": form.enabled.data,
        "name": form.name.data,
        "description": form.description.data,
        "geometry_id": form.geometry_id.data,
        "start_datetime": form.start_datetime.data,
        "start_condition_type": form.start_condition_type.data,
        "observation_days": form.observation_days.data,
        "forecast_days": form.forecast_days.data,
        "user": get_current_user(),
        "border_conditions": retrieve_series(form),
        "plan_series_list": retrieve_plan_series(form),
    }

    if form.start_condition_type.data == "initial_flows":
        params["initial_flows"] = create_initial_flows_from_form(form)


    start_condition_type = form.start_condition_type.data
    restart_file_data = form.restart_file.data
    project_file_data = form.project_file.data
    plan_file_data = form.plan_file.data

    return create(params, start_condition_type, restart_file_data, project_file_data, plan_file_data)


def get_schedule_tasks(name=None, user_first_name=None, user_last_name=None, start_condition_type=None, date_from=None,
                       date_to=None, enabled=None, frequency=None, calibration_id=None,calibration_id_for_simulations=None):
    with get_session() as session:
        query = session.query(ScheduledTask).order_by(ScheduledTask.id.desc())
        if name is not None:
            query = query.filter(func.lower(ScheduledTask.name).like(func.lower(f"%{name}%")))
        if user_first_name is not None or user_last_name is not None:
            query = query.join(User, aliased=True)
            if user_first_name is not None:
                query = query.filter(func.lower(User.first_name).like(func.lower(f"%{user_first_name}%")))
            if user_last_name is not None:
                query = query.filter(func.lower(User.last_name).like(func.lower(f"%{user_last_name}%")))
        if start_condition_type is not None and start_condition_type != "":
            query = query.filter(ScheduledTask.start_condition_type == start_condition_type)
        if date_from is not None:
            query = query.filter(ScheduledTask.start_datetime >= date_from)
        if date_to is not None:
            query = query.filter(ScheduledTask.start_datetime <= date_to)
        if enabled is not None:
            query = query.filter(ScheduledTask.enabled == enabled)
        if frequency is not None:
            query = query.filter(ScheduledTask.frequency == frequency)
        if calibration_id is not None:
            query = query.filter(ScheduledTask.calibration_id == calibration_id)
        if calibration_id_for_simulations is not None:
            query = query.filter(ScheduledTask.calibration_id_for_simulations == calibration_id_for_simulations)
        return query.all()


def get_schedule_task_config(schedule_config_id):
    with get_session() as session:
        return (
            session.query(ScheduledTask)
            .filter(ScheduledTask.id == schedule_config_id)
            .first()
        )


def delete_scheduled_task(scheduled_task_id):
    try:
        scheduled_task = get_schedule_task_config(scheduled_task_id)

        file_storage_service.delete_scheduled_task(scheduled_task_id)

        # - Esto tira una excepcion. -
        with get_session() as session:
            session.delete(scheduled_task)
            session.commit()
        return True
    except Exception as e:
        print("error while deleting scheduled task: " + scheduled_task_id)
        print(e)
        raise e
