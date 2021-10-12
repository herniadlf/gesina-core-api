from http import HTTPStatus
from flask import Flask, jsonify, redirect, url_for
from os import environ
from celery import Celery


from src.encoders import CustomJSONEncoder
from src.service.backoffice_user_service import current_user
from src.controller import (
    BACKOFFICE_BLUEPRINT,
    BACKOFFICE_USER_BLUEPRINT,
)
from src.exception_handler import set_up_exception_handlers
from src.translations import gettext, pretty_date

app = Flask(__name__)


environ.setdefault('CELERY_CONFIG_MODULE', 'src.celery_config')

celery_app = Celery()
celery_app.config_from_envvar('CELERY_CONFIG_MODULE')

app.register_blueprint(BACKOFFICE_BLUEPRINT, url_prefix="/backoffice")
app.register_blueprint(BACKOFFICE_USER_BLUEPRINT, url_prefix="/backoffice_user")

app.jinja_env.globals.update(gettext=gettext)
app.jinja_env.globals.update(pretty_date=pretty_date)
app.jinja_env.globals.update(current_user=current_user)


@app.route("/health-check")
def health_check():
    result = add.delay(1, 2)
    resultado = result.get(timeout=1)
    return jsonify({"status": resultado}), HTTPStatus.OK


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):
    return redirect(url_for("backoffice_controller.home")), HTTPStatus.MOVED_PERMANENTLY


@celery_app.task
def add(x, y):
    return x + y

@celery_app.task
def tsum(*args, **kwargs):
    print(args)
    print(kwargs)
    return sum(args[0])


app.json_encoder = CustomJSONEncoder

set_up_exception_handlers(app)

if __name__ == "__main__":
    app.run(debug=True)
