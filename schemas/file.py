from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    download_url: str


class FileListItem(BaseModel):
    name: str
    id: str
    updated_at: str
    created_at: str
    size: int
    content_type: str


class FileDeleteResponse(BaseModel):
    file_name: str


class FileListResponse(BaseModel):
    files: list[FileListItem]
