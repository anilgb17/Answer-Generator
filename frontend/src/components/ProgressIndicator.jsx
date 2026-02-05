import React from 'react'

const ProgressIndicator = ({ progress = 0, status = 'processing', message = '' }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'bg-blue-600'
      case 'complete':
        return 'bg-green-600'
      case 'error':
        return 'bg-red-600'
      default:
        return 'bg-gray-600'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'processing':
        return 'Processing...'
      case 'complete':
        return 'Complete!'
      case 'error':
        return 'Error'
      default:
        return 'Waiting...'
    }
  }

  return (
    <div className="w-full">
      <style>{`
        @keyframes glow {
          0%, 100% {
            text-shadow: 0 0 20px rgba(59, 130, 246, 0.5),
                         0 0 40px rgba(59, 130, 246, 0.3),
                         0 0 60px rgba(59, 130, 246, 0.2);
            opacity: 0.8;
          }
          50% {
            text-shadow: 0 0 30px rgba(59, 130, 246, 0.8),
                         0 0 60px rgba(59, 130, 246, 0.6),
                         0 0 90px rgba(59, 130, 246, 0.4);
            opacity: 1;
          }
        }
        @keyframes glowWaiting {
          0%, 100% {
            text-shadow: 0 0 20px rgba(156, 163, 175, 0.5),
                         0 0 40px rgba(156, 163, 175, 0.3),
                         0 0 60px rgba(156, 163, 175, 0.2);
            opacity: 0.7;
          }
          50% {
            text-shadow: 0 0 30px rgba(156, 163, 175, 0.8),
                         0 0 60px rgba(156, 163, 175, 0.6),
                         0 0 90px rgba(156, 163, 175, 0.4);
            opacity: 1;
          }
        }
        .glow-text {
          animation: glow 2s ease-in-out infinite;
          font-size: 3rem;
          font-weight: 800;
          letter-spacing: 0.1em;
          color: #d4af37;
          text-transform: uppercase;
        }
        .glow-text-waiting {
          animation: glowWaiting 2s ease-in-out infinite;
          font-size: 3rem;
          font-weight: 800;
          letter-spacing: 0.1em;
          color: #9ca3af;
          text-transform: uppercase;
        }
      `}</style>

      {/* Glowing Text Animation for Processing */}
      {status === 'processing' && (
        <div className="flex flex-col items-center justify-center py-12 mb-6">
          <div className="glow-text">
            PROCESSING {progress}%
          </div>
          <p className="mt-4 text-sm text-gray-600">{message || 'Please wait while we generate your answers...'}</p>
        </div>
      )}

      {/* Glowing Text Animation for Waiting */}
      {status !== 'processing' && status !== 'complete' && status !== 'error' && (
        <div className="flex flex-col items-center justify-center py-12 mb-6">
          <div className="glow-text-waiting">
            WAITING {progress}%
          </div>
          <p className="mt-4 text-sm text-gray-600">{message || 'Waiting to start processing...'}</p>
        </div>
      )}

      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ease-out ${getStatusColor()}`}
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        >
          {status === 'processing' && progress < 100 && (
            <div className="h-full w-full animate-pulse" />
          )}
        </div>
      </div>
    </div>
  )
}

export default ProgressIndicator
