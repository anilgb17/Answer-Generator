import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FileUploader from '../FileUploader'

describe('FileUploader Component', () => {
  let mockOnFileSelect

  beforeEach(() => {
    mockOnFileSelect = jest.fn()
  })

  test('renders upload area with instructions', () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} />)
    
    expect(screen.getByText(/Drop your question paper here/i)).toBeInTheDocument()
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument()
    expect(screen.getByText(/Supported formats: TXT, PDF, PNG, JPG/i)).toBeInTheDocument()
  })

  test('accepts valid file upload', async () => {
    const { container } = render(<FileUploader onFileSelect={mockOnFileSelect} />)
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const input = container.querySelector('input[type="file"]')
    
    await userEvent.upload(input, file)
    
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file)
      expect(screen.getByText('test.txt')).toBeInTheDocument()
    })
  })

  test('rejects file exceeding size limit', async () => {
    const { container } = render(<FileUploader onFileSelect={mockOnFileSelect} />)
    
    // Create a file larger than 10MB
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.txt', { type: 'text/plain' })
    const input = container.querySelector('input[type="file"]')
    
    await userEvent.upload(input, largeFile)
    
    await waitFor(() => {
      expect(screen.getByText(/File size exceeds 10MB limit/i)).toBeInTheDocument()
      expect(mockOnFileSelect).toHaveBeenCalledWith(null)
    })
  })

  test('rejects unsupported file format', async () => {
    const { container } = render(<FileUploader onFileSelect={mockOnFileSelect} />)
    
    const invalidFile = new File(['test'], 'test.doc', { type: 'application/msword' })
    const input = container.querySelector('input[type="file"]')
    
    // Manually trigger the change event since userEvent.upload might not work with invalid files
    Object.defineProperty(input, 'files', {
      value: [invalidFile],
      writable: false,
    })
    fireEvent.change(input)
    
    await waitFor(() => {
      expect(screen.getByText(/Unsupported file format/i)).toBeInTheDocument()
      expect(mockOnFileSelect).toHaveBeenCalledWith(null)
    })
  })

  test('allows file removal', async () => {
    const { container } = render(<FileUploader onFileSelect={mockOnFileSelect} />)
    
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const input = container.querySelector('input[type="file"]')
    
    await userEvent.upload(input, file)
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument()
    })
    
    const removeButton = screen.getByText(/Remove file/i)
    fireEvent.click(removeButton)
    
    await waitFor(() => {
      expect(screen.queryByText('test.pdf')).not.toBeInTheDocument()
      expect(mockOnFileSelect).toHaveBeenCalledWith(null)
    })
  })

  test('disables interaction when disabled prop is true', () => {
    const { container } = render(<FileUploader onFileSelect={mockOnFileSelect} disabled={true} />)
    
    // Find the main drop zone div (the one with border-2 border-dashed)
    const dropZone = container.querySelector('.border-dashed')
    expect(dropZone).toHaveClass('opacity-50')
    expect(dropZone).toHaveClass('cursor-not-allowed')
  })

  test('handles drag and drop', async () => {
    const { container } = render(<FileUploader onFileSelect={mockOnFileSelect} />)
    
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const dropZone = container.querySelector('.border-dashed')
    
    fireEvent.dragEnter(dropZone, {
      dataTransfer: { files: [file] }
    })
    
    expect(dropZone).toHaveClass('border-blue-500')
    
    fireEvent.drop(dropZone, {
      dataTransfer: { files: [file] }
    })
    
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file)
    })
  })
})
