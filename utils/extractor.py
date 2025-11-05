from pathlib import Path

import pptx
import pymupdf4llm
from docx import Document

from utils.logger import get_logger

logger = get_logger()


def extract_pdf_data(input_pdf_path: str, output_dir: str, file_id: str) -> str:
    """Extracts text and images from a PDF and saves Markdown with the given file_id."""
    try:
        # Convert output_dir to Path early and keep it as Path
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Use Path for image directory
        image_dir = output_dir_path / f"images_{file_id}"
        image_dir.mkdir(exist_ok=True)

        pages = pymupdf4llm.to_markdown(
            input_pdf_path,
            write_images=True,
            page_chunks=True,
            image_format="png",
            dpi=300,
            image_path=str(image_dir),  # pymupdf4llm expects str
            extract_words=True,
        )

        logger.info(
            "Extracted pages from PDF using pymupdf4llm", extra={"file_id": file_id}
        )

        all_text = ""
        for page in pages:
            page_text = page.get("text", "") or ""
            page_number = page.get("page_number", "Unknown")
            if page_text.strip():
                all_text += f"## Page {page_number}\n\n{page_text}\n\n"
            else:
                logger.warning(
                    "No text extracted from page",
                    extra={"file_id": file_id, "page_number": page_number},
                )

        # Build output path using Path
        output_md_path = output_dir_path / f"{file_id}.md"

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(all_text if all_text.strip() else "# No content extracted\n")

        logger.info(
            "Markdown saved successfully",
            extra={"file_id": file_id, "markdown_path": str(output_md_path)},
        )
        return str(output_md_path)

    except Exception as e:
        logger.error(
            "Error extracting PDF data", extra={"file_id": file_id, "error": str(e)}
        )
        raise ValueError(f"Failed to extract PDF: {str(e)}")


def extract_docx_data(input_docx_path: str, output_dir: str, file_id: str) -> str:
    """Extract text from DOCX and save as Markdown."""
    try:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        doc = Document(input_docx_path)
        all_text = "\n\n".join(
            [para.text for para in doc.paragraphs if para.text.strip()]
        )

        output_md_path = output_dir_path / f"{file_id}.md"
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(all_text if all_text.strip() else "# No content extracted\n")

        logger.info(
            "DOCX extracted to Markdown",
            extra={"file_id": file_id, "path": str(output_md_path)},
        )
        return str(output_md_path)

    except Exception as e:
        logger.error(
            "DOCX extraction failed", extra={"file_id": file_id, "error": str(e)}
        )
        raise ValueError(f"Failed to extract DOCX: {e}")


def extract_pptx_data(input_pptx_path: str, output_dir: str, file_id: str) -> str:
    """Extract text from PPTX and save as Markdown."""
    try:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        prs = pptx.Presentation(input_pptx_path)
        all_text = []

        for slide_num, slide in enumerate(prs.slides, start=1):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text = shape.text.strip()
                    if text:
                        slide_text.append(text)
            if slide_text:
                all_text.append(f"## Slide {slide_num}\n\n" + "\n\n".join(slide_text))

        full_text = "\n\n".join(all_text)
        output_md_path = output_dir_path / f"{file_id}.md"

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(full_text if full_text.strip() else "# No content extracted\n")

        logger.info(
            "PPTX extracted to Markdown",
            extra={"file_id": file_id, "path": str(output_md_path)},
        )
        return str(output_md_path)

    except Exception as e:
        logger.error(
            "PPTX extraction failed", extra={"file_id": file_id, "error": str(e)}
        )
        raise ValueError(f"Failed to extract PPTX: {e}")
