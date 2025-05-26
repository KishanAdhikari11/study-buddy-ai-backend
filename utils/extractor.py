import pymupdf4llm
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_data(input_pdf_path: str, output_dir: str) -> str:
    """Extracts text and images from a PDF and returns the path to the saved Markdown file."""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        image_dir = output_dir / "images"
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

        logger.debug(f"Pages data: {pages}")

        all_text = ""
        for page in pages:
            page_text = page.get('text', '') or ''
            page_number = page.get('page_number', 'Unknown')
            if page_text.strip():
                all_text += f"## Page {page_number}\n\n{page_text}\n\n"
            else:
                logger.warning(f"No text extracted for page {page_number}")

        output_md_path = output_dir / "output.md"
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(all_text if all_text else "# No content extracted\n")

        logger.info(f"Markdown saved to {output_md_path}")
        return str(output_md_path)

    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise ValueError(f"Failed to extract PDF: {str(e)}")