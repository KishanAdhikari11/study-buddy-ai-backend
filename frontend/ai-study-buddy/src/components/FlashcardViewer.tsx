// components/FlashcardViewer.tsx
'use client';
import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, RotateCcw } from 'lucide-react';
import { FlashcardData } from './FlashcardGenerator'; // Import FlashcardData interface

// Interfaces for better type safety (already defined, but repeated for clarity within this file's context)
interface Flashcard {
  id: string;
  term: string;
  definition: string;
}

interface FlashcardViewerProps {
  flashcards: FlashcardData; // This prop is guaranteed to be FlashcardData by the parent (page.tsx)
  onBack: () => void;
  uploadedFileName: string | null;
}

const FlashcardViewer: React.FC<FlashcardViewerProps> = ({ flashcards, onBack, uploadedFileName }) => {
  const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState<number>(0);
  const [isFlipped, setIsFlipped] = useState<boolean>(false);

  // Safely get the total number of flashcards
  const totalFlashcards = flashcards?.flashcards?.length || 0;

  // Effect to reset index and flip state if flashcards data changes or becomes empty
  React.useEffect(() => {
    if (currentFlashcardIndex >= totalFlashcards && totalFlashcards > 0) {
      setCurrentFlashcardIndex(0); // Reset to first card if current index is out of bounds
    } else if (totalFlashcards === 0) {
      setCurrentFlashcardIndex(0); // Ensure index is 0 if no cards
      setIsFlipped(false); // Ensure card is not flipped if no cards
    }
  }, [flashcards, totalFlashcards]); // Dependencies: re-run effect if flashcards data or total count changes

  // Handler to flip the current flashcard
  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  // Handler to navigate to the next flashcard
  const goToNextCard = () => {
    setIsFlipped(false); // Flip card back to term side when navigating
    setCurrentFlashcardIndex((prevIndex) =>
      (prevIndex + 1) % totalFlashcards // Cycle through cards
    );
  };

  // Handler to navigate to the previous flashcard
  const goToPrevCard = () => {
    setIsFlipped(false); // Flip card back to term side when navigating
    setCurrentFlashcardIndex((prevIndex) =>
      (prevIndex - 1 + totalFlashcards) % totalFlashcards // Cycle through cards, handling negative index
    );
  };

  // Handler to restart the flashcard viewing session (resets to first card)
  const restartFlashcards = () => {
    setCurrentFlashcardIndex(0);
    setIsFlipped(false);
    // If you wanted to go back to the FlashcardGenerator to create new ones:
    // onBack();
  };

  // Safely access the current flashcard object
  const currentFlashcard = flashcards?.flashcards[currentFlashcardIndex] || null;

  return (
    <section className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-inter p-4 sm:p-6 lg:p-8 relative">
      <div className="container mx-auto px-4 py-16 text-center max-w-4xl">
        <button
          onClick={onBack}
          className="absolute top-4 left-4 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded-lg shadow-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 flex items-center"
        >
          <span className="mr-2">&larr;</span> Back
        </button>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500 rounded-lg p-2">
          Your Flashcards
        </h1>
        {uploadedFileName && (
          <p className="text-md text-gray-600 dark:text-gray-400 mb-6">
            Based on: <span className="font-semibold">{uploadedFileName}</span>
          </p>
        )}

        {/* Display flashcards if available, otherwise a message */}
        {totalFlashcards > 0 && currentFlashcard ? (
          <div className="mt-8">
            {/* The interactive flashcard container */}
            <div
              className={`relative w-full max-w-md h-64 mx-auto perspective-1000 cursor-pointer rounded-xl shadow-lg transition-all duration-500 ease-in-out`}
              onClick={handleFlip}
              style={{
                transformStyle: 'preserve-3d', // Enables 3D transformations for children
                transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)', // Apply flip rotation
              }}
            >
              {/* Front of the card (Term) */}
              <div
                className={`absolute w-full h-full bg-white dark:bg-gray-700 rounded-xl flex items-center justify-center p-6 backface-hidden`}
              >
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 text-center">
                  {currentFlashcard.term}
                </p>
              </div>

              {/* Back of the card (Definition) */}
              <div
                className={`absolute w-full h-full bg-indigo-100 dark:bg-indigo-900 rounded-xl flex items-center justify-center p-6 backface-hidden rotate-y-180`}
              >
                <p className="text-xl text-gray-800 dark:text-gray-200 text-center">
                  {currentFlashcard.definition}
                </p>
              </div>
            </div>

            {/* Navigation and status for flashcards */}
            <div className="mt-6 flex justify-center items-center gap-4">
              <button
                onClick={(e) => { e.stopPropagation(); goToPrevCard(); }} // Stop propagation to prevent card flip
                disabled={totalFlashcards <= 1} // Disable if only one card
                className="p-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ArrowLeft size={24} />
              </button>
              <span className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                {currentFlashcardIndex + 1} / {totalFlashcards} {/* Current card / Total cards */}
              </span>
              <button
                onClick={(e) => { e.stopPropagation(); goToNextCard(); }} // Stop propagation to prevent card flip
                disabled={totalFlashcards <= 1} // Disable if only one card
                className="p-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ArrowRight size={24} />
              </button>
            </div>
            <button
              onClick={restartFlashcards}
              className="mt-6 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 w-auto flex items-center justify-center mx-auto"
            >
              <RotateCcw className="mr-3" size={20} /> Start Over
            </button>
          </div>
        ) : (
          // Message displayed if no flashcards are available
          <p className="mt-8 text-lg text-gray-600 dark:text-gray-400">
            No flashcards to display. Please go back and generate some.
          </p>
        )}
      </div>
    </section>
  );
};

export default FlashcardViewer;
