import React, { useState } from 'react'

const AnswerPreview = ({ answers = [], progress = 0, status = 'idle', onRequestChange }) => {
  const [editingIndex, setEditingIndex] = useState(null)
  const [changeRequest, setChangeRequest] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleEditClick = (index) => {
    setEditingIndex(index)
    setChangeRequest('')
  }

  const handleCancelEdit = () => {
    setEditingIndex(null)
    setChangeRequest('')
  }

  const handleSubmitChange = async (index) => {
    if (!changeRequest.trim()) return
    
    setIsSubmitting(true)
    try {
      if (onRequestChange) {
        await onRequestChange(index, changeRequest)
      }
      setEditingIndex(null)
      setChangeRequest('')
    } catch (error) {
      console.error('Error submitting change request:', error)
    } finally {
      setIsSubmitting(false)
    }
  }
  // Show loading animation when processing but no answers yet
  if (status === 'processing' && (!answers || answers.length === 0)) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="relative inline-block">
            <div className="w-24 h-24 border-8 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold text-blue-600">{progress}%</span>
            </div>
          </div>
          <p className="text-lg font-semibold text-gray-700 mt-6 animate-pulse">
            Generating Answers...
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Please wait while we process your questions
          </p>
        </div>
      </div>
    )
  }

  // Show empty state when idle
  if (status === 'idle' || !answers || answers.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <div className="text-center">
          <svg className="mx-auto h-24 w-24 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-lg">Answers will appear here</p>
          <p className="text-sm mt-2">Upload a file and start processing to see live preview</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Generated Answers Preview</h3>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="font-medium">{progress}%</span>
        </div>
      </div>

      {answers.map((answer, index) => (
        <div 
          key={index}
          className="bg-white rounded-lg shadow-md p-6 border border-gray-200 animate-fadeIn"
        >
          <div className="flex items-start space-x-3 mb-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
              {index + 1}
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 mb-2">Question {index + 1}</h4>
              <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
                {answer.question}
              </p>
            </div>
          </div>

          {answer.answer && (
            <div className="mt-4 pl-11">
              <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-600">
                <div className="flex items-start justify-between mb-2">
                  <h5 className="font-medium text-blue-900">Answer:</h5>
                  {editingIndex !== index && (
                    <button
                      onClick={() => handleEditClick(index)}
                      className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                      title="Request changes to this answer"
                    >
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      <span>Edit</span>
                    </button>
                  )}
                </div>
                <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                  {answer.answer}
                </p>
              </div>

              {/* Edit Interface */}
              {editingIndex === index && (
                <div className="mt-3 bg-white rounded-lg border-2 border-blue-300 p-4 animate-slideDown">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Request changes (e.g., "make it simpler", "add more details", "make it shorter")
                  </label>
                  <div className="space-y-3">
                    <textarea
                      value={changeRequest}
                      onChange={(e) => setChangeRequest(e.target.value)}
                      placeholder="Example: Make this answer simpler and easier to understand"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      rows="3"
                      disabled={isSubmitting}
                    />
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleSubmitChange(index)}
                        disabled={!changeRequest.trim() || isSubmitting}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          changeRequest.trim() && !isSubmitting
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                      >
                        {isSubmitting ? (
                          <span className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Processing...</span>
                          </span>
                        ) : (
                          'Submit Request'
                        )}
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        disabled={isSubmitting}
                        className="px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => setChangeRequest('Make this answer simpler and easier to understand')}
                        className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
                      >
                        Make simpler
                      </button>
                      <button
                        onClick={() => setChangeRequest('Add more details and examples')}
                        className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
                      >
                        Add details
                      </button>
                      <button
                        onClick={() => setChangeRequest('Make this answer shorter and more concise')}
                        className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
                      >
                        Make shorter
                      </button>
                      <button
                        onClick={() => setChangeRequest('Explain this in a more technical way')}
                        className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
                      >
                        More technical
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {answer.diagrams && answer.diagrams.length > 0 && (
            <div className="mt-4 pl-11">
              <p className="text-sm text-gray-600 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {answer.diagrams.length} diagram(s) included
              </p>
            </div>
          )}

          {!answer.answer && (
            <div className="mt-4 pl-11">
              <div className="flex items-center space-x-2 text-gray-500 text-sm">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>Generating answer...</span>
              </div>
            </div>
          )}
        </div>
      ))}

      {status === 'processing' && (
        <div className="text-center py-8">
          <div className="inline-flex items-center space-x-2 text-gray-600">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <span>Processing more questions...</span>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}

export default AnswerPreview
