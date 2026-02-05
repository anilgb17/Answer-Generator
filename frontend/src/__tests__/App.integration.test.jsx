import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import * as api from '../services/api'

// Mock the API module
jest.mock('../services/api')

describe('App Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('complete upload flow', async () => {
    // Mock API responses
    api.uploadFile.mockResolvedValue({
      session_id: 'test-session-123',
      status: 'processing'
    })

    api.getStatus.mockResolvedValue({
      status: 'complete',
      progress: 100,
      message: 'Processing complete'
    })

    render(<App />)

    // Verify initial state
    expect(screen.getByText(/Question Answer Generator/i)).toBeInTheDocument()
    expect(screen.getByText(/Upload Question Paper/i)).toBeInTheDocument()

    // Upload a file
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const input = document.querySelector('input[type="file"]')
    
    await userEvent.upload(input, file)

    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument()
    })

    // Wait for language selector to load
    await waitFor(() => {
      const englishElements = screen.queryAllByText(/English/i)
      expect(englishElements.length).toBeGreaterThan(0)
    })

    // Submit the form
    const submitButton = screen.getByText(/Generate Answers/i)
    fireEvent.click(submitButton)

    // Verify API was called
    await waitFor(() => {
      expect(api.uploadFile).toHaveBeenCalledWith(
        file,
        expect.any(String)
      )
    })

    // Wait for processing to complete
    await waitFor(() => {
      expect(screen.getByText(/Your answers are ready/i)).toBeInTheDocument()
    }, { timeout: 5000 })

    // Verify download button appears
    expect(screen.getByText(/Download PDF/i)).toBeInTheDocument()
  })

  test('language selection flow', async () => {
    render(<App />)

    // Wait for language selector to load
    await waitFor(() => {
      const englishElements = screen.queryAllByText(/English/i)
      expect(englishElements.length).toBeGreaterThan(0)
    })

    // Open language dropdown
    const button = screen.getByRole('button', { name: /Select Language/i })
    fireEvent.click(button)

    // Select Spanish
    await waitFor(() => {
      const spanishOption = screen.getByText(/Español/i)
      fireEvent.click(spanishOption)
    })

    // Verify Spanish is selected (button should show Spanish)
    await waitFor(() => {
      const spanishElements = screen.queryAllByText(/Español/i)
      expect(spanishElements.length).toBeGreaterThan(0)
    })
  })

  test.skip('download flow', async () => {
    // Mock successful download
    const mockBlob = new Blob(['test pdf'], { type: 'application/pdf' })
    api.downloadPDF.mockResolvedValue(mockBlob)

    // Mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn(() => 'blob:mock-url')
    global.URL.revokeObjectURL = jest.fn()

    // Mock document.createElement to track download link
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn(),
    }
    const originalCreateElement = document.createElement.bind(document)
    document.createElement = jest.fn((tagName) => {
      if (tagName === 'a') {
        return mockLink
      }
      return originalCreateElement(tagName)
    })

    // Mock API responses for upload and status
    api.uploadFile.mockResolvedValue({
      session_id: 'test-session-123',
      status: 'processing'
    })

    api.getStatus.mockResolvedValue({
      status: 'complete',
      progress: 100,
      message: 'Processing complete'
    })

    render(<App />)

    // Upload file
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const input = document.querySelector('input[type="file"]')
    await userEvent.upload(input, file)

    // Wait for language to load
    await waitFor(() => {
      const englishElements = screen.queryAllByText(/English/i)
      expect(englishElements.length).toBeGreaterThan(0)
    })

    // Submit
    const submitButton = screen.getByText(/Generate Answers/i)
    fireEvent.click(submitButton)

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(/Your answers are ready/i)).toBeInTheDocument()
    }, { timeout: 5000 })

    // Click download
    const downloadButton = screen.getByText(/Download PDF/i)
    fireEvent.click(downloadButton)

    // Verify download was triggered
    await waitFor(() => {
      expect(api.downloadPDF).toHaveBeenCalledWith('test-session-123')
    })

    // Cleanup
    document.createElement = originalCreateElement
  })

  test('error handling', async () => {
    // Mock API error
    api.uploadFile.mockRejectedValue({
      title: 'Upload Failed',
      message: 'Network error occurred',
      severity: 'error'
    })

    render(<App />)

    // Upload file
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const input = document.querySelector('input[type="file"]')
    await userEvent.upload(input, file)

    // Wait for language to load
    await waitFor(() => {
      const englishElements = screen.queryAllByText(/English/i)
      expect(englishElements.length).toBeGreaterThan(0)
    })

    // Submit
    const submitButton = screen.getByText(/Generate Answers/i)
    fireEvent.click(submitButton)

    // Verify error is displayed
    await waitFor(() => {
      expect(screen.getByText(/Upload Failed/i)).toBeInTheDocument()
      expect(screen.getByText(/Network error occurred/i)).toBeInTheDocument()
    })

    // Verify retry button is available
    expect(screen.getByText(/Try Again/i)).toBeInTheDocument()
  })

  test('file validation errors', async () => {
    render(<App />)

    // Try to upload an invalid file
    const invalidFile = new File(['test'], 'test.doc', { type: 'application/msword' })
    const input = document.querySelector('input[type="file"]')
    
    Object.defineProperty(input, 'files', {
      value: [invalidFile],
      writable: false,
    })
    fireEvent.change(input)

    // Verify error message
    await waitFor(() => {
      expect(screen.getByText(/Unsupported file format/i)).toBeInTheDocument()
    })

    // Verify submit button is disabled (no file selected)
    await waitFor(() => {
      const englishElements = screen.queryAllByText(/English/i)
      expect(englishElements.length).toBeGreaterThan(0)
    })

    const submitButton = screen.getByText(/Generate Answers/i)
    expect(submitButton).toBeDisabled()
  })

  test('missing file or language prevents submission', async () => {
    render(<App />)

    // Wait for language to load
    await waitFor(() => {
      const englishElements = screen.queryAllByText(/English/i)
      expect(englishElements.length).toBeGreaterThan(0)
    })

    // Try to submit without file
    const submitButton = screen.getByText(/Generate Answers/i)
    expect(submitButton).toBeDisabled()

    // Upload file
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const input = document.querySelector('input[type="file"]')
    await userEvent.upload(input, file)

    // Now button should be enabled
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled()
    })
  })
})
