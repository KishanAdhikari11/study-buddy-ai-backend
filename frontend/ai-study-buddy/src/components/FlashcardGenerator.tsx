// components/FlashcardGenerator.tsx
'use client'; // Ensure this is a client component for interactivity
import React, { useState } from 'react';
import { Loader2 } from 'lucide-react'; // Added Loader2 for loading indicator

interface FlashcardGeneratorProps {
  uploadedFile: File | null;
  onBack: () => void;
}

const FlashcardGenerator: React.FC<FlashcardGeneratorProps> = ({ uploadedFile, onBack }) => {
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [generatedContent, setGeneratedContent] = useState<string | null>(null);

  const processFlashcardsWithAI = async (): Promise<void> => {
    if (!uploadedFile) {
      setMessage('No file uploaded. Please go back to upload a file.');
      return;
    }

    setIsLoading(true);
    setMessage('Processing file with AI to generate flashcards...');
    setGeneratedContent(null);

    try {
      const promptText = `Generate a list of flashcards (term and definition) based on the content from the uploaded document. Provide at least 10-15 flashcards. Each flashcard should be clearly formatted as "Term: [Term]\nDefinition: [Definition]".`;

      // IMPORTANT: In a real application, you'd send the 'uploadedFile' to a backend
      // for secure and efficient PDF content extraction/processing.
      // The backend would then make the call to the Gemini API.
      // For this client-side example, we'll use a generic placeholder for the document content.
      const dummyPdfContentPlaceholder = "The uploaded PDF discusses key historical events in the French Revolution, including the storming of the Bastille, the Reign of Terror, and the rise of Napoleon. It also details prominent figures like Robespierre and Danton. Create flashcards covering these events and figures.";

      let chatHistory = [];
      chatHistory.push({
        role: "user",
        parts: [
          { text: promptText },
          { text: `Document content for reference: ${dummyPdfContentPlaceholder}` }
        ]
      });

      const payload = { contents: chatHistory };
      const apiKey = ""; // Canvas will automatically provide this; leave as ""
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (result.candidates && result.candidates.length > 0 && result.candidates[0].content && result.candidates[0].content.parts && result.candidates[0].content.parts.length > 0) {
        const aiGeneratedText = result.candidates[0].content.parts[0].text;
        setMessage('✨ Flashcards generated successfully!');
        setGeneratedContent(aiGeneratedText);
        console.log("Generated Flashcards from Gemini:", aiGeneratedText);
      } else {
        setMessage('Failed to get flashcard response from AI. Please try again.');
        console.error("Gemini API flashcard response error:", result);
      }
    } catch (error) {
      setMessage('Error during AI flashcard generation. Please try again.');
      console.error("AI flashcard generation error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-inter p-4 sm:p-6 lg:p-8">
      <div className="container mx-auto px-4 py-16 text-center max-w-4xl">
        <button
          onClick={onBack}
          className="absolute top-4 left-4 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded-lg shadow-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 flex items-center"
        >
          <span className="mr-2">&larr;</span> Back
        </button>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500 rounded-lg p-2">
          Generate Flashcards
        </h1>
        <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
          Click the button below to generate flashcards from your uploaded document.
        </p>

        {uploadedFile && (
          <p className="text-md text-gray-600 dark:text-gray-400 mb-6">
            Document selected: <span className="font-semibold">{uploadedFile.name}</span>
          </p>
        )}

        {/* Generate Button */}
        <button
          onClick={processFlashcardsWithAI}
          disabled={isLoading || !uploadedFile}
          className={`px-8 py-4 font-bold rounded-lg shadow-xl transition-all duration-300 transform ${
            isLoading
              ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
              : uploadedFile
              ? 'bg-purple-600 hover:bg-purple-700 text-white hover:scale-105 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50'
              : 'bg-gray-400 text-gray-700 cursor-not-allowed'
          } flex items-center justify-center mx-auto mt-8`}
        >
          {isLoading ? (
            <>
              <Loader2 className="animate-spin mr-3" size={20} /> Generating...
            </>
          ) : (
            'Generate Flashcards'
          )}
        </button>

        {/* Message Area */}
        {message && (
          <p className={`mt-4 text-md font-medium ${
            message.includes('successfully') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {message}
          </p>
        )}

        {/* Generated Content Display */}
        {generatedContent && (
          <div className="mt-8 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-inner text-left whitespace-pre-wrap max-w-2xl mx-auto">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Generated Flashcards:</h3>
            <p className="text-gray-800 dark:text-gray-200">{generatedContent}</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default FlashcardGenerator;
