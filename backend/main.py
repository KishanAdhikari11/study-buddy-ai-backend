from fastapi import FastAPI
from api.file_upload import router as file_router
from api.quizzes import router as quiz_router
from api.flashcards import router as flashcard_router
from core.config import settings

app = FastAPI(title="PDF to Quiz App", version="0.1.0")

# Include routers
app.include_router(file_router, prefix="/api/v1", tags=["file"])
app.include_router(quiz_router, prefix="/api/v1", tags=["quiz"])
app.include_router(flashcard_router, prefix="/api/v1", tags=["flashcard"])

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF to Quiz App!"}