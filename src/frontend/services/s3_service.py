import boto3
import uuid
from fastapi import UploadFile, File, HTTPException
from botocore.exceptions import ClientError

from src.frontend.config.settings import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    region_name=settings.s3_region,
)

async def upload_image(upload_type: str = "image", file: UploadFile = File(...)):
    # Проверка типа
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="file must be image-defined")

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    key = f"{upload_type}/{uuid.uuid4()}.{ext}"   # уникальное имя файла

    bucket = settings.images_bucket
    if upload_type == "anime":
        bucket = settings.anime_bucket

    try:
        contents = await file.read()
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"error to upload to the S3: {e}")

    url = f"{settings.s3_endpoint}/{bucket}/{key}"
    return {"url": url}