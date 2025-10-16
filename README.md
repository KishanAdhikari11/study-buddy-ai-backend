# AI StudyBuddy

**AI StudyBuddy** is an intelligent learning assistant designed to help students **interact with their study materials, summarize content, and learn efficiently**. Users can upload PDFs, lecture notes, and textbooks, and the AI generates **summaries, quizzes, flashcards, fill-in-the-blank exercises, and gamified learning content** to enhance memorization and engagement.

---

## Features

- **PDF & Notes Analysis**  
  Upload lecture notes, textbooks, or study material in PDF format. AI parses and understands content for further processing.

- **Automated Summaries**  
  Generate concise summaries for long documents to quickly grasp key concepts.

- **Quiz & Exercise Generation**  
  - Multiple-choice questions  
  - Fill-in-the-blank exercises  
  - Match-the-following and other gamified question types  

- **Flashcard Creation**  
  Automatically generate flashcards for memorization, supporting spaced repetition learning.

- **Gamified Learning**  
  AI generates interactive exercises and challenges to make memorization more engaging.

- **Conversational Q&A**  
  Ask questions about your notes or textbooks and get accurate AI-generated answers.

- **Document Export**  
  Download generated summaries, quizzes, and flashcards as **PDF or DOCX** for offline study.

---

## Tech Stack

- **Backend:** FastAPI / Python  
- **Frontend:** React.js / Tailwind CSS (optional)  
- **AI / NLP:** OpenAI GPT-4 / LLMs, embeddings for semantic search  
- **Database:** PostgreSQL / SQLite  
- **Storage:** Local file system / AWS S3 (for PDFs and generated content)  
- **Deployment:** Ubuntu VPS with Nginx / Gunicorn, Domain setup with HTTPS  

---

## Getting Started

### Prerequisites
- Python 3.10+  
- Node.js 18+ (if using frontend)  
- Virtual environment (optional but recommended)  

### Installation
```bash
# Clone the repo
git clone https://github.com/yourusername/ai-studybuddy.git
cd ai-studybuddy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
