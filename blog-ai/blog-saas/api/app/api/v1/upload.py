"""
Endpoint para generar presigned URLs de Cloudflare R2
"""
import os, uuid, boto3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

R2_ACCOUNT_ID   = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY   = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_KEY   = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET       = os.getenv("R2_BUCKET", "scouta-media")
R2_PUBLIC_URL   = os.getenv("R2_PUBLIC_URL", "")  # https://pub-xxx.r2.dev

ALLOWED_IMAGE = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO = {"video/mp4", "video/quicktime", "video/webm"}
MAX_IMAGE_MB = 10
MAX_VIDEO_MB = 100

class PresignRequest(BaseModel):
    filename: str
    content_type: str
    size_bytes: int

class PresignResponse(BaseModel):
    upload_url: str
    public_url: str
    key: str

def get_s3():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )

@router.post("/upload/presign", response_model=PresignResponse)
def presign_upload(
    payload: PresignRequest,
    user: User = Depends(get_current_user),
):
    ct = payload.content_type
    is_image = ct in ALLOWED_IMAGE
    is_video = ct in ALLOWED_VIDEO

    if not is_image and not is_video:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    max_bytes = (MAX_VIDEO_MB if is_video else MAX_IMAGE_MB) * 1024 * 1024
    if payload.size_bytes > max_bytes:
        label = f"{MAX_VIDEO_MB}MB" if is_video else f"{MAX_IMAGE_MB}MB"
        raise HTTPException(status_code=400, detail=f"Archivo demasiado grande (máx {label})")

    ext = payload.filename.rsplit(".", 1)[-1].lower() if "." in payload.filename else "bin"
    folder = "videos" if is_video else "images"
    key = f"{folder}/u{user.id}/{uuid.uuid4().hex}.{ext}"

    try:
        s3 = get_s3()
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": R2_BUCKET, "Key": key, "ContentType": ct},
            ExpiresIn=300,
        )
        public_url = f"{R2_PUBLIC_URL}/{key}"
        return PresignResponse(upload_url=upload_url, public_url=public_url, key=key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"R2 error: {e}")


class ModerateRequest(BaseModel):
    public_url: str
    media_type: str  # "image" | "video"
    key: str

@router.post("/upload/moderate")
def moderate_upload(
    payload: ModerateRequest,
    user: User = Depends(get_current_user),
):
    """Modera el archivo subido. Si falla, lo borra de R2."""
    from app.services.media_moderation import moderate_media
    result = moderate_media(payload.public_url, payload.media_type)
    if not result["approved"]:
        # Borrar de R2
        try:
            s3 = get_s3()
            s3.delete_object(Bucket=R2_BUCKET, Key=payload.key)
        except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Content rejected: {result['reason']}"
        )
    return {"approved": True}
