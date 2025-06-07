// components/QuizTaker.tsx
'use client';
import React, { useState, useEffect, useRef } from 'react';
import { Play, CheckCircle, XCircle, Clock, RotateCcw } from 'lucide-react';
import { QuizData } from './QuizGenerator'; // Import QuizData interface

// Interfaces for better type safety (already defined, but repeated for clarity within this file's context)
interface QuizOption {
  id: string;
  text: string;
}

interface QuizQuestion {
  id: string;
  text: string;
  options: QuizOption[];
  correctAnswer: string | string[]; // Correct answer is the 'id' of the option(s)
  type: 'single_choice' | 'multiple_choice' | 'yes_no';
}

interface QuizTakerProps {
  quiz: QuizData; // This prop is guaranteed to be QuizData by the parent (page.tsx)
  onBack: () => void;
  uploadedFileName: string | null;
}

const QuizTaker: React.FC<QuizTakerProps> = ({ quiz, onBack, uploadedFileName }) => {
  const [quizStarted, setQuizStarted] = useState<boolean>(false);
  const [quizSubmitted, setQuizSubmitted] = useState<boolean>(false);
  const [userAnswers, setUserAnswers] = useState<{ [key: string]: string | string[] }>({});
  const [score, setScore] = useState<number | null>(null);

  const [timeLeft, setTimeLeft] = useState<number>(120); // 120 seconds = 2 minutes
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Defensive check for the quiz prop: If quiz data is somehow missing, display an error
  if (!quiz) {
    console.error("QuizTaker received a null or undefined quiz prop. Displaying error state.");
    return (
      <section className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-inter p-4 sm:p-6 lg:p-8 relative">
        <div className="container mx-auto px-4 py-16 text-center max-w-4xl">
          <p className="text-xl text-red-500">Error: Quiz data not found. Please go back and generate a quiz.</p>
          <button
            onClick={onBack}
            className="mt-8 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded-lg shadow-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 flex items-center mx-auto"
          >
            <span className="mr-2">&larr;</span> Go Back
          </button>
        </div>
      </section>
    );
  }

  // Effect to manage the quiz timer
  useEffect(() => {
    if (quizStarted && !quizSubmitted) {
      // Start the timer interval
      timerIntervalRef.current = setInterval(() => {
        setTimeLeft((prevTime) => {
          if (prevTime <= 1) {
            // If time runs out, clear interval and submit quiz
            clearInterval(timerIntervalRef.current!);
            handleSubmitQuiz();
            return 0;
          }
          return prevTime - 1; // Decrement time
        });
      }, 1000); // Update every second
    } else if (!quizStarted || quizSubmitted) {
      // If quiz is not started or already submitted, clear any active timer
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    }
    // Cleanup function: runs when component unmounts or dependencies change
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, [quizStarted, quizSubmitted]); // Dependencies: re-run effect if these states change

  // Function to start the quiz
  const startQuiz = () => {
    setQuizStarted(true);
    setQuizSubmitted(false);
    setUserAnswers({}); // Reset user answers
    setScore(null); // Reset score
    setTimeLeft(120); // Reset timer to 2 minutes
  };

  // Handler for when a user changes an answer (radio button or checkbox)
  const handleAnswerChange = (questionId: string, optionId: string) => {
    setUserAnswers((prevAnswers) => {
      const question = quiz.questions.find(q => q.id === questionId);
      if (!question) return prevAnswers; // Should not happen if data is well-formed

      if (question.type === 'multiple_choice') {
        // For multiple choice, toggle the selected option in an array
        const currentSelected = (prevAnswers[questionId] || []) as string[];
        if (currentSelected.includes(optionId)) {
          return {
            ...prevAnswers,
            [questionId]: currentSelected.filter((id) => id !== optionId), // Remove if already selected
          };
        } else {
          return {
            ...prevAnswers,
            [questionId]: [...currentSelected, optionId], // Add if not selected
          };
        }
      } else {
        // For single choice/yes_no, simply set the selected option
        return {
          ...prevAnswers,
          [questionId]: optionId,
        };
      }
    });
  };

  // Function to submit the quiz and calculate score
  const handleSubmitQuiz = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current); // Stop the timer
    }
    setQuizSubmitted(true); // Mark quiz as submitted
    let correctCount = 0;
    quiz.questions.forEach((question) => {
      const userAnswer = userAnswers[question.id];
      if (question.type === 'multiple_choice') {
        // For multiple choice, compare sorted arrays of selected options
        const sortedUserAnswer = Array.isArray(userAnswer) ? [...userAnswer].sort() : [];
        const sortedCorrectAnswer = Array.isArray(question.correctAnswer) ? [...question.correctAnswer].sort() : [];
        if (JSON.stringify(sortedUserAnswer) === JSON.stringify(sortedCorrectAnswer)) {
          correctCount++;
        }
      } else {
        // For single choice/yes_no, direct comparison
        if (userAnswer === question.correctAnswer) {
          correctCount++;
        }
      }
    });
    setScore(correctCount); // Set the calculated score
  };

  // Helper function to format seconds into MM:SS string
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };

  // Function to restart the quiz (goes back to generator options)
  const restartQuiz = () => {
    setQuizStarted(false);
    setQuizSubmitted(false);
    setUserAnswers({});
    setScore(null);
    setTimeLeft(120); // Reset timer state
    onBack(); // Navigate back to the QuizGenerator component
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
          {quiz.title || 'Generated Quiz'} {/* Display quiz title */}
        </h1>
        {uploadedFileName && (
          <p className="text-md text-gray-600 dark:text-gray-400 mb-6">
            Based on: <span className="font-semibold">{uploadedFileName}</span>
          </p>
        )}

        {/* Start Quiz Button (visible before quiz starts and after generation) */}
        {!quizStarted && !quizSubmitted && (
          <button
            onClick={startQuiz}
            className="px-8 py-4 font-bold rounded-lg shadow-xl transition-all duration-300 transform bg-blue-600 hover:bg-blue-700 text-white hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 flex items-center justify-center mx-auto mt-8"
          >
            <Play className="mr-3" size={20} /> Start Quiz
          </button>
        )}

        {/* Timer Display (visible while quiz is active) */}
        {quizStarted && !quizSubmitted && (
          <div className="flex items-center justify-center mt-6 text-xl font-semibold text-gray-800 dark:text-gray-200">
            <Clock className="mr-2" size={24} /> Time Left: {formatTime(timeLeft)}
          </div>
        )}

        {/* Quiz Questions Display (visible while quiz is active) */}
        {quizStarted && !quizSubmitted && (
          <div className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md text-left max-w-2xl mx-auto">
            {quiz.questions.map((question, index) => (
              <div key={question.id} className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-700">
                <p className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-3">
                  {index + 1}. {question.text}
                </p>
                <div className="flex flex-col gap-2">
                  {question.options.map((option) => (
                    <label key={option.id} className="flex items-center space-x-2 cursor-pointer text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 p-2 rounded-md transition-colors">
                      {question.type === 'multiple_choice' ? (
                        // Checkbox for multiple choice questions
                        <input
                          type="checkbox"
                          name={`question-${question.id}`}
                          value={option.id}
                          checked={Array.isArray(userAnswers[question.id]) && (userAnswers[question.id] as string[]).includes(option.id)}
                          onChange={() => handleAnswerChange(question.id, option.id)}
                          className="form-checkbox h-5 w-5 text-indigo-600 rounded focus:ring-indigo-500 dark:bg-gray-800 dark:border-gray-600"
                        />
                      ) : (
                        // Radio button for single choice or yes/no questions
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          value={option.id}
                          checked={userAnswers[question.id] === option.id}
                          onChange={() => handleAnswerChange(question.id, option.id)}
                          className="form-radio h-5 w-5 text-indigo-600 focus:ring-indigo-500 dark:bg-gray-800 dark:border-gray-600"
                        />
                      )}
                      <span>{option.text}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
            <button
              onClick={handleSubmitQuiz}
              className="mt-6 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 w-full"
            >
              Submit Quiz
            </button>
          </div>
        )}

        {/* Quiz Results Display (visible after quiz is submitted) */}
        {quizSubmitted && (
          <div className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md text-left max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Quiz Results:</h2>
            {score !== null && (
              <p className="text-2xl font-bold mb-4 text-center">
                Your Score: <span className="text-green-600">{score}</span> / {quiz.questions.length}
              </p>
            )}

            <div className="space-y-4">
              {quiz.questions.map((question, index) => {
                const userAnswer = userAnswers[question.id];
                let isCorrect = false;
                if (question.type === 'multiple_choice') {
                  const sortedUserAnswer = Array.isArray(userAnswer) ? [...userAnswer].sort() : [];
                  const sortedCorrectAnswer = Array.isArray(question.correctAnswer) ? [...question.correctAnswer].sort() : [];
                  isCorrect = JSON.stringify(sortedUserAnswer) === JSON.stringify(sortedCorrectAnswer);
                } else {
                  isCorrect = userAnswer === question.correctAnswer;
                }

                return (
                  <div key={question.id} className={`p-4 rounded-lg border-2 ${isCorrect ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'border-red-500 bg-red-50 dark:bg-red-900/20'}`}>
                    <p className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-2">
                      {index + 1}. {question.text}
                    </p>
                    <ul className="list-disc list-inside space-y-1 text-gray-800 dark:text-gray-200">
                      {question.options.map((option) => (
                        <li key={option.id} className={`flex items-center ${
                          (question.type === 'multiple_choice' && Array.isArray(question.correctAnswer) && question.correctAnswer.includes(option.id)) ||
                          (question.type !== 'multiple_choice' && question.correctAnswer === option.id)
                            ? 'text-green-600 font-bold' // Correct answer
                            : Array.isArray(userAnswer) && userAnswer.includes(option.id) || (!Array.isArray(userAnswer) && userAnswer === option.id)
                              ? 'text-red-600' // User selected and it's wrong
                              : ''
                        }`}>
                          {/* Display check/cross icons for correct/incorrect choices */}
                          {((question.type === 'multiple_choice' && Array.isArray(question.correctAnswer) && question.correctAnswer.includes(option.id)) ||
                            (question.type !== 'multiple_choice' && question.correctAnswer === option.id)) && <CheckCircle size={16} className="inline mr-1 text-green-600" />}
                          {((Array.isArray(userAnswer) && userAnswer.includes(option.id)) || (!Array.isArray(userAnswers[question.id]) && userAnswer === option.id)) &&
                           !((question.type === 'multiple_choice' && Array.isArray(question.correctAnswer) && question.correctAnswer.includes(option.id)) ||
                           (question.type !== 'multiple_choice' && question.correctAnswer === option.id)) && <XCircle size={16} className="inline mr-1 text-red-600" />}
                          {option.text}
                        </li>
                      ))}
                    </ul>
                    {!isCorrect && (
                      <p className="mt-2 text-sm text-red-700 dark:text-red-300">
                        Correct Answer{Array.isArray(question.correctAnswer) ? 's' : ''}:{' '}
                        {Array.isArray(question.correctAnswer)
                          ? question.correctAnswer.map(id => question.options.find(opt => opt.id === id)?.text).join(', ')
                          : question.options.find(opt => opt.id === question.correctAnswer)?.text}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
            <button
              onClick={restartQuiz}
              className="mt-6 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 w-full flex items-center justify-center"
            >
              <RotateCcw className="mr-3" size={20} /> Retake Quiz
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

export default QuizTaker;
