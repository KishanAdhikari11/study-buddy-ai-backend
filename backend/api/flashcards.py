from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List
from utils.flashcards import generate_flashcards
from core.config import settings
from pydantic import BaseModel
from pathlib import Path
import logging
import genanki

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class FlashcardRequest(BaseModel):
    file_id: str
    num_cards: int = 5

def generate_anki_deck(flashcards: List[dict], file_id: str, output_dir: Path) -> str:
    deck_id = hash(f"flashcards_{file_id}") % (10**10)
    deck = genanki.Deck(deck_id, f"Flashcards_{file_id}")
    model = genanki.Model(
        model_id=deck_id + 1,
        name="Flashcard Model",
        fields=[{"name": "Question"}, {"name": "Answer"}],
        templates=[{
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": "{{Answer}}"
        }]
    )

    for card in flashcards:
        note = genanki.Note(model=model, fields=[card['question'], card['answer']])
        deck.add_note(note)

    anki_path = output_dir / f"flashcards_{file_id}.apkg"
    genanki.Package(deck).write_to_file(str(anki_path))
    logger.info(f"Generated Anki deck at {anki_path}")
    return str(anki_path)

@router.post("/generate-flashcards")
async def generate_flashcards_endpoint(request: FlashcardRequest):
    try:
        flashcard_data = generate_flashcards(request.file_id, request.num_cards)
        flashcards = flashcard_data.get("flashcards", [])
        
        if not flashcards:
            logger.error(f"Failed to generate flashcards for file_id: {request.file_id}")
            raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {flashcard_data.get('error', 'No flashcards generated')}")

        # Generate Anki deck
        output_dir = Path(settings.OUTPUT_DIR)
        anki_path = generate_anki_deck(flashcards, request.file_id, output_dir)
        
        logger.info(f"Flashcards generated for file_id: {request.file_id}")
        return {
            "flashcards": flashcards,
            "anki_file": anki_path
        }
    except Exception as e:
        logger.error(f"Error generating flashcards for file_id: {request.file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@router.get("/download-anki/{file_id}")
async def download_anki_deck(file_id: str):
    anki_path = Path(settings.OUTPUT_DIR) / f"flashcards_{file_id}.apkg"
    if not anki_path.exists():
        logger.error(f"Anki deck not found: {anki_path}")
        raise HTTPException(status_code=404, detail="Anki deck not found")
    return FileResponse(str(anki_path), filename=f"flashcards_{file_id}.apkg")