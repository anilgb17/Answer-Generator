import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import DownloadButton from '../DownloadButton'

// Mock fetch
global.fetch = jest.fn()

describe('DownloadButton Component', () => {
  let mockOnDownloadStart
  let mockOnDownloadComplete
  let mockOnDownloadError

  beforeEach(() => {
    mockOnDownloadStart = jest.fn()
    mockOnDownloadComplete = jest.fn()
    mockOnDownloadError = jest.fn()
    global.fetch.mockClear()
    
    // Mock URL.createObjectURL and revokeObjectURL
    global.URL.createObjectURL = jest.fn(() => 'blob:mock-url')
    global.URL.revokeObjectURL = jest.fn()
  })

  test('renders download button', () => {
    render(
      <DownloadButton
        sessionId="test-session"
        onDownloadStart={mockOnDownloadStart}
        onDownloadComplete={mockOnDownloadComplete}
        onDownloadError={mockOnDownloadError}
      />
    )
    
    expect(screen.getByText('Download PDF')).toBeInTheDocument()
  })

  test('is disabled when no sessionId provided', () => {
    render(
      <DownloadButton
        sessionId={null}
        onDownloadStart={mockOnDownloadStart}
        onDownloadComplete={mockOnDownloadComplete}
        onDownloadError={mockOnDownloadError}
      />
    )
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  test('is disabled when disabled prop is true', () => {
    render(
      <DownloadButton
        sessionId="test-session"
        disabled={true}
        onDownloadStart={mockOnDownloadStart}
        onDownloadComplete={mockOnDownloadComplete}
        onDownloadError={mockOnDownloadError}
      />
    )
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  test('handles successful download', async () => {
    const mockBlob = new Blob(['test pdf content'], { type: 'application/pdf' })
    global.fetch.mockResolvedValueOnce({
      ok: true,
      blob: () => Promise.resolve(mockBlob)
    })

    render(
      <DownloadButton
        sessionId="test-session"
        onDownloadStart={mockOnDownloadStart}
        onDownloadComplete={mockOnDownloadComplete}
        onDownloadError={mockOnDownloadError}
      />
    )
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(mockOnDownloadStart).toHaveBeenCalled()
    })
    
    await waitFor(() => {
      expect(mockOnDownloadComplete).toHaveBeenCalled()
    })
  })

  test('handles download error', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'))

    render(
      <DownloadButton
        sessionId="test-session"
        onDownloadStart={mockOnDownloadStart}
        onDownloadComplete={mockOnDownloadComplete}
        onDownloadError={mockOnDownloadError}
      />
    )
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(mockOnDownloadError).toHaveBeenCalled()
    })
  })

  test('shows downloading state', async () => {
    global.fetch.mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        blob: () => Promise.resolve(new Blob(['test']))
      }), 100))
    )

    render(
      <DownloadButton
        sessionId="test-session"
        onDownloadStart={mockOnDownloadStart}
        onDownloadComplete={mockOnDownloadComplete}
        onDownloadError={mockOnDownloadError}
      />
    )
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Downloading...')).toBeInTheDocument()
    })
  })
})
