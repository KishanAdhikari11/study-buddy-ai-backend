from pathlib import Path
import logging
import pymupdf4llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_data(input_pdf_path: str, output_dir: str, file_id: str) -> str:
    """Extracts text and images from a PDF and saves Markdown with the given file_id."""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        image_dir = output_dir / f"images_{file_id}"  # Unique image directory per file_id
        image_dir.mkdir(exist_ok=True)

        pages = pymupdf4llm.to_markdown(
            input_pdf_path,
            write_images=True,
            page_chunks=True,
            image_format="png",
            dpi=300,
            image_path=str(image_dir),
            extract_words=True
        )

        logger.debug(f"Pages data for file_id {file_id}: {pages}")

        all_text = ""
        for page in pages:
            page_text = page.get('text', '') or ''
            page_number = page.get('page_number', 'Unknown')
            if page_text.strip():
                all_text += f"## Page {page_number}\n\n{page_text}\n\n"
            else:
                logger.warning(f"No text extracted for page {page_number} in file_id {file_id}")

        output_md_path = output_dir / f"{file_id}.md"  # Save as output_<file_id>.md
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(all_text if all_text else "# No content extracted\n")

        logger.info(f"Markdown saved to {output_md_path} for file_id {file_id}")
        return str(output_md_path)

    except Exception as e:
        logger.error(f"Error extracting PDF for file_id {file_id}: {str(e)}")
        raise ValueError(f"Failed to extract PDF: {str(e)}")
    
def extract_docx_data(input_docx_path: str, output_dir: str, file_id: str) -> str:
    """Extracts text from a DOCX file and saves it as Markdown with the given file_id."""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        docx_content = pymupdf4llm.to_markdown(
            input_docx_path,
            write_images=False,
            page_chunks=True
        )

        logger.debug(f"DOCX content for file_id {file_id}: {docx_content}")

        output_md_path = output_dir / f"{file_id}.md"  # Save as output_<file_id>.md
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(docx_content if docx_content else "# No content extracted\n")

        logger.info(f"Markdown saved to {output_md_path} for file_id {file_id}")
        return str(output_md_path)

    except Exception as e:
        logger.error(f"Error extracting DOCX for file_id {file_id}: {str(e)}")
        raise ValueError(f"Failed to extract DOCX: {str(e)}")
    
def extract_pptx_data(input_pptx_path: str, output_dir: str, file_id: str) -> str:
    """Extracts text from a PPTX file and saves it as Markdown with the given file_id."""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        pptx_content = pymupdf4llm.to_markdown(
            input_pptx_path,
            write_images=False,
            page_chunks=True
        )

        logger.debug(f"PPTX content for file_id {file_id}: {pptx_content}")

        output_md_path = output_dir / f"{file_id}.md"  # Save as output_<file_id>.md
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(pptx_content if pptx_content else "# No content extracted\n")

        logger.info(f"Markdown saved to {output_md_path} for file_id {file_id}")
        return str(output_md_path)

    except Exception as e:
        logger.error(f"Error extracting PPTX for file_id {file_id}: {str(e)}")
        raise ValueError(f"Failed to extract PPTX: {str(e)}")
    
    