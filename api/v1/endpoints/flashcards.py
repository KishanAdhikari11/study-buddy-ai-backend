# routers/flashcards.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict # Import Dict
from utils.flashcards import generate_flashcards # This will be updated
from core.config import settings
from pydantic import BaseModel, Field # Import Field
from pathlib import Path
import logging
import genanki

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class FlashcardRequest(BaseModel):
    file_id: str
    total_flashcards: int = Field(5, gt=0, description="Number of flashcards to generate (must be greater than 0)") # Renamed and added validation
    language: str = Field("en", description="Desired language for flashcard questions and answers (e.g., 'en', 'es', 'fr')") # New field

def generate_anki_deck(flashcards: List[Dict], file_id: str, language: str, output_dir: Path) -> str:
    """
    Generates an Anki deck (.apkg) file from a list of flashcards.
    
    Args:
        flashcards (List[Dict]): A list of dictionaries, where each dictionary
                                 contains 'question' and 'answer' keys.
        file_id (str): The unique ID of the source file, used for naming the deck.
        language (str): The language of the flashcards, can be used for deck title.
        output_dir (Path): The directory where the .apkg file will be saved.

    Returns:
        str: The file path to the generated Anki deck.
    """
    deck_name = f"{language.upper()} Flashcards from {file_id}" # Incorporate language
    # Using a more robust ID hashing, ensuring it's positive
    deck_id = abs(hash(f"flashcards_{file_id}_{language}")) % (10**10)
    
    deck = genanki.Deck(deck_id, deck_name)
    
    # Model ID should be different from deck ID but also deterministic
    model_id = abs(hash(f"flashcard_model_{language}")) % (10**10)
    model = genanki.Model(
        model_id=model_id,
        name=f"Simple Flashcard Model ({language.upper()})",
        fields=[{"name": "Question"}, {"name": "Answer"}],
        templates=[{
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": "{{Answer}}"
        }],
        css="""
            .card {
             font-family: sans-serif;
             font-size: 20px;
             text-align: center;
             color: black;
             background-color: white;
            }
            .night_mode .card {
             color: white;
             background-color: black;
            }
        """
    )

    for card in flashcards:
        # Ensure 'question' and 'answer' keys exist
        question = card.get('question', 'No Question')
        answer = card.get('answer', 'No Answer')
        note = genanki.Note(model=model, fields=[question, answer])
        deck.add_note(note)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    anki_filename = f"flashcards_{file_id}_{language}.apkg" # Include language in filename
    anki_path = output_dir / anki_filename
    
    genanki.Package(deck).write_to_file(str(anki_path))
    logger.info(f"Generated Anki deck at {anki_path}")
    return str(anki_path)

@router.post("/generate-flashcards")
async def generate_flashcards_endpoint(request: FlashcardRequest):
    try:
        # Pass num_cards and language to the utility function
        flashcard_data = generate_flashcards(
            file_id=request.file_id,
            num_cards=request.total_flashcards,
            language=request.language # Pass the language
        )
        flashcards = flashcard_data.get("flashcards", [])
        
        if not flashcards:
            logger.error(f"Failed to generate flashcards for file_id: {request.file_id}, language: {request.language}")
            raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {flashcard_data.get('error', 'No flashcards generated')}")

        # Generate Anki deck, passing the language
        output_dir = Path(settings.OUTPUT_DIR)
        anki_path = generate_anki_deck(
            flashcards=flashcards,
            file_id=request.file_id,
            language=request.language, # Pass the language to Anki generator
            output_dir=output_dir
        )
        
        logger.info(f"Flashcards generated for file_id: {request.file_id}, language: {request.language}")
        return {
            "flashcards": flashcards,
            "anki_file": anki_path
        }
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Error generating flashcards for file_id: {request.file_id}, language: {request.language}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards: {str(e)}")

@router.get("/download-anki/{file_id}/{language}") # Add language to path
async def download_anki_deck(file_id: str, language: str): # Receive language
    anki_filename = f"flashcards_{file_id}_{language}.apkg" # Construct filename
    anki_path = Path(settings.OUTPUT_DIR) / anki_filename
    if not anki_path.exists():
        logger.error(f"Anki deck not found: {anki_path}")
        raise HTTPException(status_code=404, detail="Anki deck not found. Please ensure flashcards were generated for this language and file.")
    return FileResponse(str(anki_path), filename=anki_filename)