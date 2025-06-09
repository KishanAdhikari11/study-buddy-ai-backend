// components/HeroSection.tsx
'use client'; // Ensure this is a client component for interactivity
import React, { useState, DragEvent, ChangeEvent } from 'react';
import { UploadCloud, CheckCircle } from 'lucide-react';

// Define props for HeroSection
interface HeroSectionProps {
  onFileReady: (file: File | null) => void; // Explicitly allow null for invalid files
  onGenerateQuizClick: () => void;
  onGenerateFlashcardClick: () => void;
  uploadedFile: File | null;
}

const HeroSection: React.FC<HeroSectionProps> = ({
  onFileReady,
  onGenerateQuizClick,
  onGenerateFlashcardClick,
  uploadedFile,
}) => {
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

  // Handle drag enter event
  const handleDragEnter = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragOver(true);
  };

  // Handle drag leave event
  const handleDragLeave = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragOver(false);
  };

  // Handle drag over event
  const handleDragOver = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault(); // Essential to allow a drop
    setIsDragOver(true);
  };

  // Handle drop event
  const handleDrop = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  // Handle file input change event
  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  // Process the selected or dropped file
  const handleFile = (file: File): void => {
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setMessage('File size exceeds 10MB limit.');
      onFileReady(null); // Inform parent about no valid file
      return;
    }
    // Only allow PDF for this example; add other types as supported by your backend
    if (file.type !== 'application/pdf') {
      setMessage('Only PDF files are supported.');
      onFileReady(null); // Inform parent about no valid file
      return;
    }
    // Safely call onFileReady using optional chaining
    onFileReady?.(file); // Fixed: Use optional chaining to ensure it's a function before calling
    setMessage(`File "${file.name}" uploaded successfully!`);
    console.log("File uploaded:", file);
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-inter p-4 sm:p-6 lg:p-8">
      <div className="container mx-auto px-4 py-16 text-center max-w-4xl">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-500 rounded-lg p-2">
          AI Study Buddy
        </h1>
        <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
          Transform your PDFs into powerful learning tools. Our AI effortlessly converts your study materials into interactive quizzes and insightful flashcards, making revision smarter and more effective.
        </p>

        {/* Drag and Drop Area */}
        <div
          className={`border-2 border-dashed ${
            isDragOver ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-300 dark:border-gray-700'
          } rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all duration-300 ease-in-out cursor-pointer hover:border-indigo-400 dark:hover:border-indigo-600 mb-8`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload-input')?.click()}
          style={{ minHeight: '200px' }}
        >
          {uploadedFile ? (
            <div className="text-center text-green-600 dark:text-green-400">
              <CheckCircle size={48} className="mx-auto mb-4" />
              <p className="font-semibold text-lg">{uploadedFile.name}</p>
              <p className="text-sm">Ready for processing.</p>
            </div>
          ) : (
            <>
              <UploadCloud size={48} className="text-gray-400 dark:text-gray-500 mb-4" />
              <p className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Upload or drag and drop a PDF file
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Max file size is 10MB. Only PDF files.
              </p>
            </>
          )}
          <input
            id="file-upload-input"
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleFileInputChange}
          />
        </div>

        {/* Message Area */}
        {message && (
          <p className={`mt-4 text-sm font-medium ${
            message.includes('successfully') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {message}
          </p>
        )}

        <div className="mt-8 flex flex-wrap justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <span className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full">.pdf</span>
          <span className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full">.docx (Future)</span>
          <span className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full">.txt (Future)</span>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-4 mt-8">
          <button
            onClick={onGenerateQuizClick}
            disabled={!uploadedFile}
            className={`px-6 py-3 font-semibold rounded-lg shadow-md transition-all duration-300 transform ${
              uploadedFile
                ? 'bg-indigo-600 hover:bg-indigo-700 text-white hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50'
                : 'bg-gray-400 text-gray-700 cursor-not-allowed'
            }`}
          >
            Generate Quiz
          </button>
          <button
            onClick={onGenerateFlashcardClick}
            disabled={!uploadedFile}
            className={`px-6 py-3 font-semibold rounded-lg shadow-md transition-all duration-300 transform ${
              uploadedFile
                ? 'bg-purple-600 hover:bg-purple-700 text-white hover:scale-105 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50'
                : 'bg-gray-400 text-gray-700 cursor-not-allowed'
            }`}
          >
            Generate Flashcard
          </button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
