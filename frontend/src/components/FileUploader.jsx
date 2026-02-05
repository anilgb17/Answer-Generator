import React, { useState, useRef } from 'react'
import { ArrowUpTrayIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

const FileUploader = ({ onFileSelect, disabled = false }) => {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const SUPPORTED_FORMATS = ['.txt', '.pdf', '.png', '.jpg', '.jpeg']
  const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

  const validateFile = (file) => {
    setError(null)

    if (!file) {
      setError('No file selected')
      return false
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      setError(`File size exceeds 10MB limit. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB`)
      return false
    }

    // Check file format
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
    if (!SUPPORTED_FORMATS.includes(fileExtension)) {
      setError(`Unsupported file format. Supported formats: ${SUPPORTED_FORMATS.join(', ')}`)
      return false
    }

    return true
  }

  const handleFile = (file) => {
    if (validateFile(file)) {
      setSelectedFile(file)
      onFileSelect(file)
    } else {
      setSelectedFile(null)
      onFileSelect(null)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (disabled) return

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (disabled) return

    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleButtonClick = () => {
    if (!disabled) {
      fileInputRef.current?.click()
    }
  }

  return (
    <div className="w-full">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center
          transition-colors duration-200
          ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-blue-400'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleChange}
          accept={SUPPORTED_FORMATS.join(',')}
          disabled={disabled}
        />

        <div className="flex flex-col items-center space-y-4">
          {selectedFile ? (
            <>
              <DocumentTextIcon className="w-16 h-16 text-green-500" />
              <div>
                <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
              {!disabled && (
                <button
                  type="button"
                  className="text-sm text-blue-600 hover:text-blue-700"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedFile(null)
                    setError(null)
                    onFileSelect(null)
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ''
                    }
                  }}
                >
                  Remove file
                </button>
              )}
            </>
          ) : (
            <>
              <ArrowUpTrayIcon className="w-16 h-16 text-gray-400" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Drop your question paper here
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse
                </p>
              </div>
              <p className="text-xs text-gray-400">
                Supported formats: TXT, PDF, PNG, JPG (max 10MB)
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  )
}

export default FileUploader
