import uuid

from fastapi import UploadFile

from utils.logger import get_logger
from utils.supabase_client import get_supabase_client

logger = get_logger()


async def upload_file_to_supabase(
    file: UploadFile, bucket_name: str, file_id: uuid.UUID, user_id: uuid.UUID
) -> str:
    supabase = get_supabase_client()
    storage_path = f"{user_id}/{file_id}/{file.filename}"
    file_data = await file.read()
    try:
        supabase.storage.from_(bucket_name).upload(
            storage_path,
            file_data,
            file_options={"content-type": file.content_type, "cacheControl": "3600"},
        )
        return storage_path

    except Exception as e:
        logger.error("File Upload Error", extra={"error": e})
        raise Exception(f"Failed to upload file: {str(e)}")


def delete_file_from_supabase(file_name: list[str], bucket_name: str) -> None:
    """
    Deletes a file from the specified Supabase storage bucket.
    Args:
        file_name (str): The name of the file to be deleted.
        bucket_name (str): The name of the Supabase storage bucket.
    """
    try:
        supabase = get_supabase_client()
        supabase.storage.from_(bucket_name).remove(file_name)

    except Exception as e:
        raise Exception(f"Failed to delete file: {str(e)}")


def list_files_in_supabase(bucket_name: str, user_id: str) -> list[dict]:
    """
    Lists all files in the specified Supabase storage bucket.
    Args:
        bucket_name (str): The name of the Supabase storage bucket.
        user_id (str): The user ID to list files for.
    """
    all_files = []
    try:
        supabase = get_supabase_client()
        folders = supabase.storage.from_(bucket_name).list(user_id)
        for folder in folders:
            folder_name = folder["name"]
            folder_path = f"{user_id}/{folder_name}/"
            files = supabase.storage.from_(bucket_name).list(folder_path)
            for file in files:
                all_files.append(
                    {
                        "name": file["name"],
                        "id": file["id"],
                        "updated_at": file["updated_at"],
                        "created_at": file["created_at"],
                        "size": file["metadata"]["size"],
                        "content_type": file["metadata"]["mimetype"],
                    }
                )
        return all_files

    except Exception as e:
        raise Exception(f"Failed to list files: {str(e)}")
