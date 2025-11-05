import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from core.security import get_current_user
from core.settings import settings
from utils.extractor import (
    extract_docx_data,
    extract_pdf_data,
    extract_pptx_data,
)
from utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file uploads for PDF, DOCX, and PPTX formats, saves them,
    and then extracts content into Markdown format.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name")

    file_extension = Path(file.filename).suffix.lower()
    allowed_extensions = {".pdf", ".docx", ".pptx", ".md", ".txt"}

    if file_extension not in allowed_extensions:
        logger.error(
            "Invalid file type uploaded", extra={"file_extension": file_extension}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(allowed_extensions)} files are allowed",
        )

    file_id = str(uuid.uuid4())
    upload_dir = settings.UPLOAD_DIR or "uploads"
    file_path = Path(upload_dir) / f"{file_id}{file_extension}"

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info("File saved", extra={"file_path": file_path})
    except Exception as e:
        logger.error("Error saving file", exc_info=e)
        raise HTTPException(status_code=500, detail="Error saving file")

    markdown_path = None
    try:
        if file_extension == ".pdf":
            markdown_path = extract_pdf_data(
                str(file_path), settings.OUTPUT_DIR, file_id
            )
        elif file_extension == ".docx":
            markdown_path = extract_docx_data(
                str(file_path), settings.OUTPUT_DIR, file_id
            )
        elif file_extension == ".pptx":
            markdown_path = extract_pptx_data(
                str(file_path), settings.OUTPUT_DIR, file_id
            )
        elif file_extension in {".md", ".txt"}:
            text_content = content.decode("utf-8")  # reuse already-read bytes
            output_dir_path = Path(settings.OUTPUT_DIR)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            markdown_path = str(output_dir_path / f"{file_id}.md")
            with open(markdown_path, "w", encoding="utf-8") as md_file:
                md_file.write(text_content)

        if markdown_path:
            logger.info(
                "File processed",
                extra={
                    "file_id": file_id,
                    "file_extension": file_extension,
                    "markdown_path": markdown_path,
                },
            )
            return {
                "file_id": file_id,
                "message": f"File uploaded and processed successfully as Markdown from {file_extension}",
                "markdown_path": markdown_path,
            }

        raise HTTPException(status_code=500, detail="Failed to process file")

    except Exception as e:
        logger.error(
            "Error processing file",
            extra={"file_extension": file_extension, "file_id": file_id, "error": e},
        )
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
