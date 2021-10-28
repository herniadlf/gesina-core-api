from flask import Blueprint, render_template, request, redirect, url_for
import io
from minio import Minio


GEOMETRY_BLUEPRINT = Blueprint("geometry_controller", __name__)


@GEOMETRY_BLUEPRINT.route("/")
@GEOMETRY_BLUEPRINT.route("")
def new():
    return render_template("new_geometry.html")


# POC subir archivo
# @GEOMETRY_BLUEPRINT.route("/", methods=["POST"])
# @GEOMETRY_BLUEPRINT.route("", methods=["POST"])
# def save():
#     # check if the post request has the file part
#     if 'file' not in request.files:
#         print('No file part')
#         return redirect(request.url)
#     file = request.files['file']
#     # If the user does not select a file, the browser submits an
#     # empty file without a filename.
#     if file.filename == '':
#         print('No selected file')
#         return redirect(request.url)
#     if file:
#         minio_client = Minio(
#             endpoint="localhost:9000",
#             access_key="minioadmin",
#             secret_key="password",
#             secure=False,
#         )
#         file_bytes = file.read()
#         data = io.BytesIO(file_bytes)
#         minio_client.put_object("geometry", file.filename, data, len(file_bytes))
#
#         return redirect(request.url)
#
#     return redirect(request.url)

@GEOMETRY_BLUEPRINT.route("/", methods=["POST"])
@GEOMETRY_BLUEPRINT.route("", methods=["POST"])
def save():



    return redirect(url_for("geometry.new"))
