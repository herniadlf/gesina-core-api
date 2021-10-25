from flask import Blueprint, jsonify
from http import HTTPStatus
import os
import io
from minio import Minio


GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)


@GEOMETRY_BLUEPRINT.route("/", methods=["POST"])
@GEOMETRY_BLUEPRINT.route("", methods=["POST"])
def save():
    minio_client = Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )

    localpath = os.path.dirname(__file__)
    filename = "prueba.txt"
    filepath = os.path.join(localpath, filename)

    with open(filepath, "r") as el_file:
        file_bytes = el_file.read().encode("utf-8")
        data = io.BytesIO(file_bytes)

        minio_client.put_object("geometry", "blabla2.g01", data, len(file_bytes))

    return jsonify({"exists": "ok"}), HTTPStatus.OK
