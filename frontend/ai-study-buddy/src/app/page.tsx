// app/page.tsx
'use client'; // This directive makes this a Client Component

import React, { useState } from 'react';
// Ensure these paths correctly reflect your file structure:
// components/HeroSection.tsx should be located at app/components/HeroSection.tsx
import HeroSection from '@/components/HeroSection';
import QuizGenerator, { QuizData } from '@/components/QuizGenerator';
import QuizTaker from '@/components/QuizTaker';
import FlashcardGenerator, { FlashcardData } from '@/components/FlashcardGenerator';
import FlashcardViewer from '@/components/FlashcardViewer';

// Define the different views/states of our application
type AppView = 'hero' | 'quiz-generator' | 'quiz-taker' | 'flashcard-generator' | 'flashcard-viewer';

export default function HomePage() {
  const [currentView, setCurrentView] = useState<AppView>('hero');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [generatedQuiz, setGeneratedQuiz] = useState<QuizData | null>(null);
  const [generatedFlashcards, setGeneratedFlashcards] = useState<FlashcardData | null>(null);

  // Callback from HeroSection when a file is ready
  const handleFileReady = (file: File | null) => {
    setUploadedFile(file);
    // When a new file is uploaded, reset any generated content
    setGeneratedQuiz(null);
    setGeneratedFlashcards(null);
  };

  // Callback from QuizGenerator when a quiz is generated
  const handleQuizGenerated = (quiz: QuizData) => {
    setGeneratedQuiz(quiz);
    setCurrentView('quiz-taker'); // Move to QuizTaker view
  };

  // Callback from FlashcardGenerator when flashcards are generated
  const handleFlashcardsGenerated = (flashcards: FlashcardData) => {
    setGeneratedFlashcards(flashcards);
    setCurrentView('flashcard-viewer'); // Move to FlashcardViewer view
  };

  // Render the appropriate component based on the currentView state
  const renderContent = () => {
    switch (currentView) {
      case 'hero':
        return (
          <HeroSection
            onFileReady={handleFileReady}
            onGenerateQuizClick={() => setCurrentView('quiz-generator')}
            onGenerateFlashcardClick={() => setCurrentView('flashcard-generator')}
            uploadedFile={uploadedFile}
          />
        );
      case 'quiz-generator':
        return (
          <QuizGenerator
            uploadedFile={uploadedFile}
            onBack={() => setCurrentView('hero')}
            onQuizGenerated={handleQuizGenerated}
          />
        );
      case 'quiz-taker':
        // Ensure generatedQuiz exists before rendering QuizTaker
        if (!generatedQuiz) {
          // If for some reason we land here without a generated quiz, go back to generator
          setCurrentView('quiz-generator');
          return null;
        }
        return (
          <QuizTaker
            quiz={generatedQuiz}
            onBack={() => setCurrentView('quiz-generator')} // Go back to generator options
            uploadedFileName={uploadedFile ? uploadedFile.name : null}
          />
        );
      case 'flashcard-generator':
        return (
          <FlashcardGenerator
            uploadedFile={uploadedFile}
            onBack={() => setCurrentView('hero')}
            onFlashcardsGenerated={handleFlashcardsGenerated}
          />
        );
      case 'flashcard-viewer':
        // Ensure generatedFlashcards exists before rendering FlashcardViewer
        if (!generatedFlashcards) {
          // If for some reason we land here without generated flashcards, go back to generator
          setCurrentView('flashcard-generator');
          return null;
        }
        return (
          <FlashcardViewer
            flashcards={generatedFlashcards}
            onBack={() => setCurrentView('flashcard-generator')} // Go back to generator options
            uploadedFileName={uploadedFile ? uploadedFile.name : null}
          />
        );
      default:
        return null;
    }
  };

  return (
    <main >
      {renderContent()}
    </main>
  );
}
