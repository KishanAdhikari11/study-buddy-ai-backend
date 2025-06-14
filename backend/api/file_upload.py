from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Depends
from core.dependencies import get_directories
from core.database import get_db
from utils.indexer import store_markdown_to_vector
from datetime import datetime
import uuid
import pymupdf4llm
from pathlib import Path
from models.file import FileInDB
import os

router = APIRouter()



@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Body(...),
    topic: str = Body(...),
    directories: dict = Depends(get_directories),
    db=Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    source_material_id = str(uuid.uuid4())
    upload_dir = directories["upload_dir"]
    output_dir = upload_dir / source_material_id
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{source_material_id}.pdf"
    markdown_path = output_dir / "output.md"

    try:
        # Save uploaded PDF
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        # Convert PDF to markdown
        markdown_text = pymupdf4llm.to_markdown(str(pdf_path), write_images=False)
        if not markdown_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        # Save markdown
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        # Store in vector database
        metadata = {"source_material_id": source_material_id, "topic": topic, "user_id": user_id}
        if not store_markdown_to_vector(str(markdown_path), metadata=metadata, user_id=user_id):
            raise HTTPException(status_code=500, detail="Failed to store PDF content in vector store")

        # Save file metadata to database
        file_data = FileInDB(
            id=source_material_id,
            user_id=user_id,
            topic=topic,
            filename=file.filename,
            file_type="pdf",
            markdown_path=str(markdown_path),
            processed=True,
            created_at=datetime.utcnow()
        )
        await db.files.insert_one(file_data.dict())

        return {"status": "success", "source_material_id": source_material_id}

    except Exception as e:
        # Clean up files if processing fails
        for path in [pdf_path, markdown_path]:
            if path.exists():
                path.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temporary files
        for path in [pdf_path, markdown_path]:
            if path.exists():
                path.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()


# Alternative approach without dependency injection:
@router.post("/upload-simple")
async def upload_pdf_simple(
    file: UploadFile = File(...),
    user_id: str = Body(...),
    topic: str = Body(...),
    db=Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    source_material_id = str(uuid.uuid4())
    upload_dir = Path("uploads")  # Define directly
    upload_dir.mkdir(exist_ok=True)
    
    output_dir = upload_dir / source_material_id
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{source_material_id}.pdf"
    markdown_path = output_dir / "output.md"

    try:
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        markdown_text = pymupdf4llm.to_markdown(str(pdf_path), write_images=False)
        if not markdown_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        metadata = {"source_material_id": source_material_id, "topic": topic, "user_id": user_id}
        if not store_markdown_to_vector(str(markdown_path), metadata=metadata, user_id=user_id):
            raise HTTPException(status_code=500, detail="Failed to store PDF content in vector store")

        file_data = FileInDB(
            id=source_material_id,
            user_id=user_id,
            topic=topic,
            filename=file.filename,
            file_type="pdf",
            markdown_path=str(markdown_path),
            processed=True,
            created_at=datetime.utcnow()
        )
        await db.files.insert_one(file_data.dict())

        return {"status": "success", "source_material_id": source_material_id}

    finally:
        for path in [pdf_path, markdown_path]:
            if path.exists():
                path.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()