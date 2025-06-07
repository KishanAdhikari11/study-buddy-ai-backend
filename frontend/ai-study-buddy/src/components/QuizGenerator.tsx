// components/QuizGenerator.tsx
'use client';
import React, { useState, ChangeEvent } from 'react';
import { ChevronDown, Loader2 } from 'lucide-react';

// Define types for quiz options and data structures
type QuizType = 'single_choice' | 'multiple_choice' | 'yes_no';
type NumberOfQuestions = 5 | 10 | 15 | 20;

interface QuizOption {
  id: string;
  text: string;
}

interface QuizQuestion {
  id: string;
  text: string;
  options: QuizOption[];
  correctAnswer: string | string[]; // Correct answer is the 'id' of the option(s)
  type: QuizType;
}

export interface QuizData { // Export this interface so QuizTaker can use it
  title: string;
  questions: QuizQuestion[];
}

interface QuizGeneratorProps {
  uploadedFile: File | null;
  onBack: () => void;
  onQuizGenerated: (quiz: QuizData) => void; // Callback to pass generated quiz data to parent
}

const QuizGenerator: React.FC<QuizGeneratorProps> = ({ uploadedFile, onBack, onQuizGenerated }) => {
  const [numberOfQuestions, setNumberOfQuestions] = useState<NumberOfQuestions>(10);
  const [quizType, setQuizType] = useState<QuizType>('single_choice');
  const [isQuizTypeDropdownOpen, setIsQuizTypeDropdownOpen] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Dummy Quiz Data (to simulate Gemini API output with requested new questions)
  const dummyQuizData: QuizData = {
    title: "AI & LLMs Basics", // Updated title to reflect new content
    questions: [
      // Original Fluid Dynamics Questions (retained for variety)
      { id: "q1", text: "What principle states that an increase in the speed of a fluid occurs simultaneously with a decrease in pressure or a decrease in the fluid's potential energy?", options: [{ id: "a", text: "Archimedes' Principle" }, { id: "b", text: "Pascal's Principle" }, { id: "c", text: "Bernoulli's Principle" }, { id: "d", text: "Newton's Third Law" }], correctAnswer: "c", type: "single_choice" },
      { id: "q2", text: "Which of the following are types of fluid flow?", options: [{ id: "a", text: "Laminar flow" }, { id: "b", text: "Turbulent flow" }, { id: "c", text: "Static flow" }, { id: "d", text: "Rotational flow" }], correctAnswer: ["a", "b"], type: "multiple_choice" },
      { id: "q3", text: "Is fluid viscosity a measure of its resistance to deformation?", options: [{ id: "true", text: "Yes" }, { id: "false", text: "No" }], correctAnswer: "true", type: "yes_no" },
      { id: "q4", text: "In a horizontal pipe, if the speed of water decreases, what happens to its pressure according to Bernoulli's principle?", options: [{ id: "a", text: "Increases" }, { id: "b", text: "Decreases" }, { id: "c", text: "Stays the same" }, { id: "d", text: "Becomes zero" }], correctAnswer: "a", type: "single_choice" },
      { id: "q5", text: "Does a non-Newtonian fluid have a constant viscosity regardless of shear rate?", options: [{ id: "true", text: "Yes" }, { id: "false", text: "No" }], correctAnswer: "false", type: "yes_no" },
      // New AI/LLM Questions (formatted to match QuizQuestion interface)
      { id: "q6", text: "What is a key ability for Language Models (LMs) according to the overview?",
        options: [
          { id: "a", text: "Short context understanding" },
          { id: "b", text: "Long context modeling" },
          { id: "c", text: "Image recognition" },
          { id: "d", text: "Code generation" }
        ],
        correctAnswer: "b", type: "single_choice" },
      { id: "q7", text: "What is Retrieval Augmented Generation (RAG) used for in the context of LLMs?",
        options: [
          { id: "a", text: "To tackle internal problems of LLMs" },
          { id: "b", text: "To retrieval grounding external context to LLMs for generation purpose" },
          { id: "c", text: "To increase the speed of pre-training" },
          { id: "d", text: "To reduce the size of LLMs" }
        ],
        correctAnswer: "b", type: "single_choice" },
      { id: "q8", text: "What is the purpose of positional encoding (PE) in attention modules?",
        options: [
          { id: "a", text: "To reduce computational complexity" },
          { id: "b", text: "To inject information about the relative and absolute position of tokens" },
          { id: "c", text: "To improve image recognition" },
          { id: "d", text: "To enhance the model's ability to perform calculations" }
        ],
        correctAnswer: "b", type: "single_choice" },
      { id: "q9", text: "What is a potential issue with extrapolating outside the training positions in positional encoding?",
        options: [
          { id: "a", text: "It always improves performance" },
          { id: "b", text: "It may produce catastrophic values" },
          { id: "c", text: "It has no effect on performance" },
          { id: "d", text: "It reduces computational cost" }
        ],
        correctAnswer: "b", type: "single_choice" },
      { id: "q10", text: "What is one of the main challenges for long context language modeling?",
        options: [
          { id: "a", text: "Pre-trained LMs have unlimited length extrapolation capabilities." },
          { id: "b", text: "The KV cache on decoding stage can lead to excessive memory." },
          { id: "c", text: "Window attention always improves quality and efficiency." },
          { id: "d", text: "Long contexts are always treated equally by LLMs." }
        ],
        correctAnswer: "b", type: "single_choice" },
    ],
  };

  // Mapping for displaying quiz types
  const quizTypeDisplayMap = {
    single_choice: 'Single Choice',
    multiple_choice: 'Multiple Choice',
    yes_no: 'Yes or No',
  };

  // Function to simulate AI quiz generation
  const processQuizWithAI = async (): Promise<void> => {
    if (!uploadedFile) {
      setMessage('No file uploaded. Please go back to upload a file.');
      return;
    }

    setIsLoading(true);
    setMessage('Processing file with AI to generate quizzes...');

    try {
      // Simulate network delay for API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Filter dummy data based on user selection for type and number of questions
      const filteredQuestions = dummyQuizData.questions
        .filter(q => q.type === quizType)
        .slice(0, numberOfQuestions);

      const generatedQuiz: QuizData = {
        ...dummyQuizData,
        questions: filteredQuestions,
      };

      setMessage('✨ Quizzes generated successfully! Redirecting to quiz...');
      onQuizGenerated(generatedQuiz); // Pass the generated quiz data to the parent component
    } catch (error) {
      setMessage('Error during AI quiz generation. Please try again.');
      console.error("AI quiz generation error:", error);
    } finally {
      setIsLoading(false);
    }
  };

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
          Generate Quizzes
        </h1>
        <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
          Customize your quiz settings and let AI create questions from your uploaded document.
        </p>

        {uploadedFile && (
          <p className="text-md text-gray-600 dark:text-gray-400 mb-6">
            Document selected: <span className="font-semibold">{uploadedFile.name}</span>
          </p>
        )}

        {/* Quiz Options Section */}
        <div className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">What kind of quiz would you like to create?</h2>

          <div className="flex flex-col sm:flex-row justify-center items-center gap-6">
            {/* Number of Questions Dropdown */}
            <div className="relative w-full sm:w-1/2">
              <label htmlFor="num-questions" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 sr-only">
                Number of questions
              </label>
              <select
                id="num-questions"
                value={numberOfQuestions}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => setNumberOfQuestions(parseInt(e.target.value) as NumberOfQuestions)}
                className="block w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white appearance-none pr-10 cursor-pointer"
                aria-label="Number of questions"
              >
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
                <option value={15}>15 Questions</option>
                <option value={20}>20 Questions</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
                <ChevronDown size={20} />
              </div>
            </div>

            {/* Type of Question(s) Dropdown */}
            <div
              className="relative w-full sm:w-1/2"
            >
              <label htmlFor="quiz-type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 sr-only">
                Type of question(s)
              </label>
              <div
                className="relative cursor-pointer"
                onBlur={() => setIsQuizTypeDropdownOpen(false)} // Close when focus leaves
                tabIndex={0} // Make it focusable
              >
                <button
                  type="button"
                  onClick={() => setIsQuizTypeDropdownOpen(!isQuizTypeDropdownOpen)}
                  className="flex justify-between items-center w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  aria-haspopup="true"
                  aria-expanded={isQuizTypeDropdownOpen ? 'true' : 'false'}
                >
                  <span>{quizTypeDisplayMap[quizType]}</span>
                  <ChevronDown className={`transform transition-transform ${isQuizTypeDropdownOpen ? 'rotate-180' : ''}`} size={20} />
                </button>
                {isQuizTypeDropdownOpen && (
                  <div className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-700 shadow-lg rounded-lg border border-gray-200 dark:border-gray-600">
                    {['single_choice', 'multiple_choice', 'yes_no'].map((type) => (
                      <div
                        key={type}
                        onClick={() => {
                          setQuizType(type as QuizType);
                          setIsQuizTypeDropdownOpen(false);
                        }}
                        className="px-4 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-900 dark:text-white first:rounded-t-lg last:rounded-b-lg"
                      >
                        {quizTypeDisplayMap[type as QuizType]}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={processQuizWithAI}
          disabled={isLoading || !uploadedFile}
          className={`px-8 py-4 font-bold rounded-lg shadow-xl transition-all duration-300 transform ${
            isLoading
              ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
              : uploadedFile
              ? 'bg-green-600 hover:bg-green-700 text-white hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50'
              : 'bg-gray-400 text-gray-700 cursor-not-allowed'
          } flex items-center justify-center mx-auto mt-8`}
        >
          {isLoading ? (
            <>
              <Loader2 className="animate-spin mr-3" size={20} /> Generating...
            </>
          ) : (
            'Generate Quizzes'
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
      </div>
    </section>
  );
};

export default QuizGenerator;
