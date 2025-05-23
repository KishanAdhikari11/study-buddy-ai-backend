from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import shutil
import os

app = FastAPI()

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    topic: str = Form(...)
):
    content_type = file.content_type
    filename = file.filename
    save_path = os.path.join("uploads", filename)

    try:
        os.makedirs("uploads", exist_ok=True)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error while saving file"})

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "message": "File uploaded successfully",
            "filename": filename,
            "content_type": content_type,
            "user_id": user_id,
            "topic": topic
        }
    )
