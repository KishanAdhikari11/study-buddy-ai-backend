from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.extractor import extract_pdf_data, extract_docx_data, extract_pptx_data # Import all extractors
from core.config import settings
from pathlib import Path
import uuid
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file uploads for PDF, DOCX, and PPTX formats, saves them,
    and then extracts content into Markdown format.
    """
    # Get the file extension
    file_extension = Path(file.filename).suffix.lower()

    # Define allowed file types
    allowed_extensions = {".pdf", ".docx", ".pptx"}

    # Check if the file type is allowed
    if file_extension not in allowed_extensions:
        logger.error(f"Invalid file type uploaded: {file_extension}")
        raise HTTPException(status_code=400, detail=f"Only {', '.join(allowed_extensions)} files are allowed")

    file_id = str(uuid.uuid4())
    # Construct file path with the original extension
    file_path = Path(settings.UPLOAD_DIR) / f"{file_id}{file_extension}"

    # Ensure upload directory exists
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    markdown_path = None
    # Extract Markdown based on file type
    try:
        if file_extension == ".pdf":
            markdown_path = extract_pdf_data(str(file_path), settings.OUTPUT_DIR, file_id)
        elif file_extension == ".docx":
            markdown_path = extract_docx_data(str(file_path), settings.OUTPUT_DIR, file_id)
        elif file_extension == ".pptx":
            markdown_path = extract_pptx_data(str(file_path), settings.OUTPUT_DIR, file_id)
        
        if markdown_path:
            logger.info(f"File {file_id} ({file_extension}) processed, Markdown saved to {markdown_path}")
            return {"file_id": file_id, "message": f"File uploaded and processed successfully as Markdown from {file_extension}"}
        else:
            logger.error(f"No extractor found for file type: {file_extension}")
            raise HTTPException(status_code=500, detail=f"Failed to process file: No extractor found for {file_extension}")

    except Exception as e:
        logger.error(f"Error processing {file_extension} file for {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

