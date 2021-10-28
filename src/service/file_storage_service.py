import io
import os

from minio import Minio

minio_url = os.getenv("MINIO_URL", "localhost:9000")
minio_user = os.getenv("MINIO_ROOT_USER", "minioadmin")
minio_password = os.getenv("MINIO_ROOT_PASSWORD", "password")


def validate_file(files_in_request):
    if "file" not in files_in_request:
        raise Exception("not a file in request")

    file = files_in_request["file"]
    if not file or file.filename == "":
        raise Exception("No selected file")


def save_geometry(file):
    minio_client = Minio(
        endpoint=minio_url,
        access_key=minio_user,
        secret_key=minio_password,
        secure=False,
    )
    file_bytes = file.read()
    data = io.BytesIO(file_bytes)
    minio_client.put_object("geometry", file.filename, data, len(file_bytes))
