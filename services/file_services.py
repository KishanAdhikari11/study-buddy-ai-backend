from utils.supabase_client import get_supabase_client


def store_file_to_supabase(file_path: str, bucket_name: str) -> str:
    """
    Uploads a file to the specified Supabase storage bucket.

    Args:
        file_path (str): The local path to the file to be uploaded.
        bucket_name (str): The name of the Supabase storage bucket.

    Returns:
        str: The public URL of the uploaded file.
    """
    supabase = get_supabase_client()
    with open(file_path, "rb") as file_data:
        file_name = file_path.split("/")[-1]
        response = supabase.storage.from_(bucket_name).upload(
            file_name, file_data, file_options={"cacheControl": "3600"}
        )

    if response.get("error"):
        raise Exception(f"Failed to upload file: {response['error']['message']}")

    public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
    return public_url


def delete_file_from_supabase(file_name: list[str], bucket_name: str) -> None:
    """
    Deletes a file from the specified Supabase storage bucket.

    Args:
        file_name (str): The name of the file to be deleted.
        bucket_name (str): The name of the Supabase storage bucket.
    """
    supabase = get_supabase_client()
    response = supabase.storage.from_(bucket_name).remove(file_name)

    if response.get("error"):
        raise Exception(f"Failed to delete file: {response['error']['message']}")


def list_files_in_supabase(bucket_name: str, folder: str) -> list[dict]:
    """
    Lists all files in the specified Supabase storage bucket.

    Args:
        bucket_name (str): The name of the Supabase storage bucket.
        folder (str): The folder path within the bucket to list files from.
    """
    supabase = get_supabase_client()
    response = supabase.storage.from_(bucket_name).list(folder=folder)

    if response.get("error"):
        raise Exception(f"Failed to list files: {response['error']['message']}")

    return response.get("data", [])
