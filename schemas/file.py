from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    content_type: str
    topic: str
    user_id: str
    detail: str