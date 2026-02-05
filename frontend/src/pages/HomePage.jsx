import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import FileUploader from '../components/FileUploader';
import LanguageSelector from '../components/LanguageSelector';
import ProgressIndicator from '../components/ProgressIndicator';
import DownloadButton from '../components/DownloadButton';
import ErrorDisplay from '../components/ErrorDisplay';
import AnswerPreview from '../components/AnswerPreview';
import { uploadFile, getStatus, downloadPDF, regenerateAnswer } from '../services/api';

export default function HomePage() {
  const { user, isAuthenticated } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [sessionId, setSessionId] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState([]);

  useEffect(() => {
    if (!sessionId || !processing) return;

    const pollInterval = setInterval(async () => {
      try {
        const statusData = await getStatus(sessionId);
        setProgress(statusData.progress || 0);
        setStatus(statusData.status);
        setStatusMessage(statusData.message || '');
        
        if (statusData.answers && statusData.answers.length > 0) {
          setAnswers(statusData.answers.map(ans => ({
            question: ans.question,
            answer: ans.answer,
            diagrams: ans.diagrams_count > 0 ? Array(ans.diagrams_count).fill({}) : []
          })));
        }

        if (statusData.status === 'complete') {
          setProcessing(false);
          clearInterval(pollInterval);
        } else if (statusData.status === 'error') {
          setProcessing(false);
          clearInterval(pollInterval);
          setError({
            title: 'Processing Error',
            message: statusData.message || 'An error occurred during processing',
            severity: 'error',
          });
        }
      } catch (err) {
        console.error('Status polling error:', err);
        setProcessing(false);
        clearInterval(pollInterval);
        setError(err);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [sessionId, processing]);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    if (!file) {
      setSessionId(null);
      setProgress(0);
      setStatus('idle');
      setStatusMessage('');
    }
  };

  const handleLanguageSelect = (language) => {
    setSelectedLanguage(language);
  };

  const handleProviderSelect = (provider) => {
    setSelectedProvider(provider);
  };

  const handleSubmit = async () => {
    if (!selectedFile || !selectedLanguage) {
      setError({
        title: 'Missing Information',
        message: 'Please select both a file and a language before submitting.',
        severity: 'warning',
      });
      return;
    }

    try {
      setError(null);
      setProcessing(true);
      setProgress(0);
      setStatus('processing');
      setStatusMessage('Uploading file...');

      const response = await uploadFile(
        selectedFile, 
        selectedLanguage.code, 
        selectedProvider,
        user?.id
      );
      setSessionId(response.session_id);
      setStatusMessage('Processing questions...');
    } catch (err) {
      console.error('Upload error:', err);
      setProcessing(false);
      setError(err);
    }
  };

  const handleRetry = () => {
    setError(null);
    setSessionId(null);
    setProgress(0);
    setStatus('idle');
    setStatusMessage('');
    setProcessing(false);
    setAnswers([]);
  };
  
  const handleRequestChange = async (questionIndex, changeRequest) => {
    if (!sessionId) return;
    
    try {
      const result = await regenerateAnswer(sessionId, questionIndex, changeRequest);
      
      setAnswers(prevAnswers => {
        const newAnswers = [...prevAnswers];
        if (newAnswers[questionIndex]) {
          newAnswers[questionIndex] = {
            ...newAnswers[questionIndex],
            answer: result.answer
          };
        }
        return newAnswers;
      });
      
      return result;
    } catch (err) {
      console.error('Error regenerating answer:', err);
      setError({
        title: 'Regeneration Failed',
        message: err.message || 'Failed to regenerate answer',
        severity: 'error',
      });
      throw err;
    }
  };

  const handleDismissError = () => {
    setError(null);
  };

  const canSubmit = selectedFile && selectedLanguage && !processing;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="text-center flex-1">
              <h1 className="text-3xl font-bold text-gray-900">
                Question Answer Generator
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Upload your questions and get comprehensive answers with visual elements
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <span className="text-sm text-gray-700">Hi, {user?.username}</span>
                  <Link
                    to="/dashboard"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Dashboard
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-4 py-2 text-indigo-600 hover:text-indigo-700"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Split Screen Layout */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-180px)]">
          {/* Left Panel - Upload & Controls */}
          <div className="bg-white rounded-xl shadow-lg p-6 overflow-y-auto space-y-6">
            {error && (
              <ErrorDisplay
                error={error}
                onRetry={handleRetry}
                onDismiss={handleDismissError}
              />
            )}

            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                1. Upload Question Paper/Questions
              </h2>
              <FileUploader
                onFileSelect={handleFileSelect}
                disabled={processing}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                2. Select AI Provider
              </h2>
              <div className="space-y-3">
                {['gemini', 'perplexity', 'openai'].map((provider) => (
                  <label
                    key={provider}
                    className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                    style={{ borderColor: selectedProvider === provider ? '#3B82F6' : '#E5E7EB' }}
                  >
                    <input
                      type="radio"
                      name="provider"
                      value={provider}
                      checked={selectedProvider === provider}
                      onChange={(e) => handleProviderSelect(e.target.value)}
                      disabled={processing}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 capitalize">{provider}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          provider === 'openai' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {provider === 'openai' ? 'PAID' : 'FREE'}
                        </span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                3. Select Language
              </h2>
              <LanguageSelector
                onLanguageSelect={handleLanguageSelect}
                disabled={processing}
              />
            </div>

            {!processing && status !== 'complete' && (
              <div className="flex justify-center pt-4">
                <button
                  onClick={handleSubmit}
                  disabled={!canSubmit}
                  className={`
                    px-8 py-3 rounded-lg font-medium text-white text-lg
                    transition-colors duration-200
                    ${canSubmit
                      ? 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                      : 'bg-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  Generate Answers
                </button>
              </div>
            )}

            {processing && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  4. Processing
                </h2>
                <ProgressIndicator
                  progress={progress}
                  status={status}
                  message={statusMessage}
                />
              </div>
            )}

            {status === 'complete' && sessionId && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  5. Download Your Answers
                </h2>
                <div className="flex flex-col items-center space-y-4">
                  <div className="text-center">
                    <p className="text-green-600 font-medium mb-2">
                      ✓ Your answers are ready!
                    </p>
                    <p className="text-gray-600 text-sm">
                      Click the button below to download your PDF
                    </p>
                  </div>
                  <DownloadButton
                    sessionId={sessionId}
                    onDownloadStart={() => console.log('Download started')}
                    onDownloadComplete={() => console.log('Download complete')}
                    onDownloadError={(err) => setError({
                      title: 'Download Failed',
                      message: err.message,
                      severity: 'error',
                    })}
                  />
                  <button
                    onClick={handleRetry}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Process another file
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Live Preview */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <AnswerPreview 
              answers={answers} 
              progress={progress} 
              status={status}
              onRequestChange={handleRequestChange}
            />
          </div>
        </div>

        <div className="text-center mt-4 text-gray-500 text-sm">
          <p>Supported formats: TXT, PDF, PNG, JPG • Max file size: 10MB</p>
        </div>
      </div>
    </div>
  );
}
