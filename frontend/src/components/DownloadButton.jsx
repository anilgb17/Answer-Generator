import React, { useState } from 'react'
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline'

const DownloadButton = ({ sessionId, disabled = false, onDownloadStart, onDownloadComplete, onDownloadError }) => {
  const [downloading, setDownloading] = useState(false)

  const handleDownload = async () => {
    if (disabled || downloading || !sessionId) return

    try {
      setDownloading(true)
      if (onDownloadStart) onDownloadStart()

      // Call the download API with full URL
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/download/${sessionId}`)
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `answers_${sessionId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      if (onDownloadComplete) onDownloadComplete()
    } catch (error) {
      console.error('Download error:', error)
      if (onDownloadError) onDownloadError(error)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <button
      onClick={handleDownload}
      disabled={disabled || downloading || !sessionId}
      className={`
        inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg
        shadow-sm text-white transition-colors duration-200
        ${
          disabled || downloading || !sessionId
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
        }
      `}
    >
      {downloading ? (
        <>
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
          Downloading...
        </>
      ) : (
        <>
          <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
          Download PDF
        </>
      )}
    </button>
  )
}

export default DownloadButton
