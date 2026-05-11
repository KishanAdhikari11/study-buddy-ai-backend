import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.settings import settings
from db import get_db
from models import EmbeddingJob, File, JobStatus, User
from schemas.common import ErrorResponseSchema
from schemas.file import (
    FileListItem,
    FileListResponse,
    FileUploadResponse,
    FileUrlResponse,
)
from services.file_service import (
    delete_file_from_supabase,
    get_pdf_url,
    upload_file_to_supabase,
)
from utils.helper import validate_file_extension
from utils.logger import get_logger
from utils.supabase_client import get_signed_url

router = APIRouter(
    responses={
        403: {"model": ErrorResponseSchema, "description": "Forbidden Response"}
    },
)
logger = get_logger()


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file: UploadFile,
    request: Request,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileUploadResponse:
    if not file.filename or file.size == 0 or file.size is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded."
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty"
        )

    try:
        ext = validate_file_extension(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    result = await db.execute(select(User).where(User.supabase_id == auth_user))
    db_user = result.scalar_one_or_none()

    if not db_user:
        db_user = User(
            supabase_id=auth_user,
            email=str(auth_user),
            name=f"user_{str(auth_user)[:6]}",
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    file_id = uuid.uuid4()

    result = await db.execute(
        select(File).where(File.filename == file.filename, File.user_id == db_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File with the same name already exists.",
        )

    try:
        storage_path = await upload_file_to_supabase(
            bucket_name=settings.SUPABASE_BUCKET,
            user_id=db_user.supabase_id,
            file_id=file_id,
            file=file,
            contents=contents,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )

    try:
        db_file = File(
            id=file_id,
            filename=file.filename,
            filepath=storage_path,
            user_id=db_user.id,
            file_type=ext,
        )
        db.add(db_file)

        job = EmbeddingJob(file_id=file_id, status=JobStatus.Pending)
        db.add(job)

        await db.commit()
        await db.refresh(db_file)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

    await request.app.state.redis.lpush("embedding_jobs", str(file_id))

    signed_url = await get_signed_url(storage_path)

    return FileUploadResponse(
        file_id=str(file_id),
        filename=file.filename,
        file_type=ext,
        download_url=signed_url,
    )


@router.get("/files", response_model=FileListResponse)
async def list_files(
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileListResponse:
    result = await db.execute(select(User).where(User.supabase_id == auth_user))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    file_query = await db.execute(select(File).where(File.user_id == db_user.id))
    db_files = file_query.scalars().all()

    file_responses = []
    for file in db_files:
        file_responses.append(
            FileListItem(
                id=str(file.id),
                name=file.filename,
                size=0,
                content_type=file.file_type,
                updated_at=file.uploaded_at.isoformat(),
            )
        )

    return FileListResponse(files=file_responses)


@router.delete("/{file_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_name: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.execute(select(User).where(User.supabase_id == auth_user))
    db_user = user.scalar_one_or_none()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    file = await db.execute(
        select(File).where(File.filename == file_name, File.user_id == db_user.id)
    )
    db_file = file.scalar_one_or_none()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    try:
        delete_file_from_supabase(
            file_name=[db_file.filepath],
            bucket_name=settings.SUPABASE_BUCKET,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )
    try:
        await db.delete(db_file)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

    return None


@router.get("/{file_name}", response_model=FileUrlResponse)
async def get_file_url(
    file_name: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileUrlResponse:
    user = await db.execute(select(User).where(User.supabase_id == auth_user))
    db_user = user.scalar_one_or_none()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    file = await db.execute(
        select(File).where(File.filename == file_name, File.user_id == db_user.id)
    )
    db_file = file.scalar_one_or_none()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No file found"
        )

    try:
        url = get_pdf_url(
            bucket_name=settings.SUPABASE_BUCKET, file_path=db_file.filepath
        )
        return FileUrlResponse(
            id=str(db_file.id),
            url=url["signedURL"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error: {str(e)}",
        )
