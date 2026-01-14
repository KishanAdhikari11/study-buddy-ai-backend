import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from core.settings import settings
from db import get_db
from models import Embedding, File, User
from schemas.common import ErrorResponseSchema
from schemas.file import (
    FileDeleteResponse,
    FileListItem,
    FileListResponse,
    FileUploadResponse,
)
from services.embeding_service import chunk_text, create_embedding
from services.file_service import (
    delete_file_from_supabase,
    list_files_in_supabase,
    upload_file_to_supabase,
)
from utils.extractor import DocumentExtractor
from utils.helper import validate_file_extension, with_temp_file
from utils.logger import get_logger
from utils.supabase_client import get_signed_url

router = APIRouter(
    responses={
        403: {"model": ErrorResponseSchema, "description": "Forbidden Response"}
    },
)
logger = get_logger()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile,
    request: Request,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileUploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded."
        )
    if file.size is None or file.size == 0:
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
        logger.error("File Upload Error- Invalid file extension", extra={"error": e})
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
    existing_file = result.scalar_one_or_none()
    if existing_file:
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
        await db.commit()
        await db.refresh(db_file)

    except Exception as e:
        await db.rollback()
        logger.error(
            "Database Error - creating user",
            extra={"error": e, "supabase_id": auth_user},
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

    signed_url = await get_signed_url(storage_path)
    try:
        suffix = "." + ext

        async def process_file(tmp_path: str):
            extractor = DocumentExtractor(tmp_path)
            text = extractor.extract()

            chunks = chunk_text(text)

            embeddings = create_embedding(
                request.app.state.embedding_model,
                chunks,
            )

            for chunk, embedding in zip(chunks, embeddings):
                emb = Embedding(
                    file_id=file_id,
                    chunks=chunk,
                    embedding=embedding,
                )
                db.add(emb)

            await db.commit()

        await with_temp_file(contents, suffix, process_file)

    except Exception as e:
        logger.error("Embedding Pipeline failed", extra={"error": str(e)})
        await db.rollback()

    return FileUploadResponse(
        file_id=str(file_id),
        filename=file.filename,
        file_type=ext,
        download_url=signed_url,
    )


@router.get("/list", response_model=FileListResponse)
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

    try:
        files = list_files_in_supabase(
            bucket_name=settings.SUPABASE_BUCKET,
            user_id=auth_user,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}",
        )

    file_responses = []
    for file in files:
        file_response = FileListItem(
            name=file["name"],
            id=file["id"],
            size=file["size"],
            content_type=file["content_type"],
            updated_at=file["updated_at"],
            created_at=file["created_at"],
        )
        file_responses.append(file_response)

    return FileListResponse(files=file_responses)


@router.delete("/delete/{file_name}", status_code=status.HTTP_200_OK)
async def delete_file(
    file_name: str,
    auth_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileDeleteResponse:
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
        await db.delete(db_file)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
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

    return FileDeleteResponse(file_name=file_name)
