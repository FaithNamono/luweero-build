"""Cloud object storage helper (S3-compatible API: Supabase Storage, AWS S3, DigitalOcean Spaces, R2...).

All credentials come from environment variables via app.config.Settings.
"""
from functools import lru_cache
from typing import BinaryIO

from app.config import get_settings


@lru_cache
def _client():
    import boto3  # imported lazily so the API boots even if storage is not configured
    from botocore.config import Config

    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.storage_endpoint_url or None,
        region_name=s.storage_region,
        aws_access_key_id=s.storage_access_key_id or None,
        aws_secret_access_key=s.storage_secret_access_key or None,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def build_blueprint_url(object_key: str | None) -> str | None:
    """Return a URL for a stored blueprint, or None when the user has no blueprint / storage is unset.

    - STORAGE_USE_SIGNED_URLS=true  -> short-lived presigned URL (private bucket, recommended for prod)
    - otherwise                     -> public URL: STORAGE_PUBLIC_BASE_URL + "/" + key
    """
    if not object_key:
        return None
    s = get_settings()
    if s.storage_use_signed_urls:
        return _client().generate_presigned_url(
            "get_object",
            Params={"Bucket": s.storage_bucket, "Key": object_key},
            ExpiresIn=s.storage_signed_url_ttl_seconds,
        )
    if not s.storage_public_base_url:
        return None
    return f"{s.storage_public_base_url.rstrip('/')}/{object_key.lstrip('/')}"


def upload_blueprint(object_key: str, fileobj: BinaryIO, content_type: str = "application/pdf") -> str:
    """Upload a blueprint file to the bucket and return its object key."""
    s = get_settings()
    _client().upload_fileobj(fileobj, s.storage_bucket, object_key, ExtraArgs={"ContentType": content_type})
    return object_key
