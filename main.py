from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from api.v1.endpoints.file_upload import router as file_router
from api.v1.endpoints.quizzes import router as quiz_router
from api.v1.endpoints.flashcards import router as flashcard_router
from core.config import settings # Assuming settings are defined here, though not directly used in this snippet

app = FastAPI(title="PDF to Quiz App", version="0.1.0")

origins = [
    "http://localhost:3000",  
    "http://localhost:8000",  

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  
)

app.include_router(file_router, prefix="/api/v1", tags=["file"])
app.include_router(quiz_router, prefix="/api/v1", tags=["quiz"])
app.include_router(flashcard_router, prefix="/api/v1", tags=["flashcard"])

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF to Quiz App!"}

