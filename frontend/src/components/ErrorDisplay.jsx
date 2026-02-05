import React from 'react'
import { XCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'

const ErrorDisplay = ({ error, onRetry, onDismiss }) => {
  if (!error) return null

  const getErrorIcon = () => {
    switch (error.severity) {
      case 'error':
        return <XCircleIcon className="h-6 w-6 text-red-500" />
      case 'warning':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
      case 'info':
        return <InformationCircleIcon className="h-6 w-6 text-blue-500" />
      default:
        return <XCircleIcon className="h-6 w-6 text-red-500" />
    }
  }

  const getErrorStyles = () => {
    switch (error.severity) {
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      case 'info':
        return 'bg-blue-50 border-blue-200'
      default:
        return 'bg-red-50 border-red-200'
    }
  }

  const getTextStyles = () => {
    switch (error.severity) {
      case 'error':
        return 'text-red-800'
      case 'warning':
        return 'text-yellow-800'
      case 'info':
        return 'text-blue-800'
      default:
        return 'text-red-800'
    }
  }

  return (
    <div className={`rounded-lg border p-4 ${getErrorStyles()}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">{getErrorIcon()}</div>
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${getTextStyles()}`}>
            {error.title || 'An error occurred'}
          </h3>
          {error.message && (
            <div className={`mt-2 text-sm ${getTextStyles()}`}>
              <p>{error.message}</p>
            </div>
          )}
          {error.details && (
            <div className={`mt-2 text-sm ${getTextStyles()}`}>
              <p className="font-mono text-xs bg-white bg-opacity-50 p-2 rounded">
                {error.details}
              </p>
            </div>
          )}
          {error.guidance && (
            <div className={`mt-2 text-sm ${getTextStyles()}`}>
              <p className="font-medium">Suggestion:</p>
              <p>{error.guidance}</p>
            </div>
          )}
          <div className="mt-4 flex space-x-3">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className={`
                  text-sm font-medium px-3 py-1.5 rounded-md
                  ${
                    error.severity === 'error'
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : error.severity === 'warning'
                      ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }
                `}
              >
                Try Again
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="text-sm font-medium text-gray-600 hover:text-gray-800"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ErrorDisplay
