import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import ErrorDisplay from '../ErrorDisplay'

describe('ErrorDisplay Component', () => {
  test('renders nothing when no error provided', () => {
    const { container } = render(<ErrorDisplay error={null} />)
    expect(container.firstChild).toBeNull()
  })

  test('displays error title and message', () => {
    const error = {
      title: 'Test Error',
      message: 'This is a test error message',
      severity: 'error'
    }
    
    render(<ErrorDisplay error={error} />)
    
    expect(screen.getByText('Test Error')).toBeInTheDocument()
    expect(screen.getByText('This is a test error message')).toBeInTheDocument()
  })

  test('displays error details when provided', () => {
    const error = {
      title: 'Error',
      message: 'Something went wrong',
      details: 'Stack trace here',
      severity: 'error'
    }
    
    render(<ErrorDisplay error={error} />)
    
    expect(screen.getByText('Stack trace here')).toBeInTheDocument()
  })

  test('displays guidance when provided', () => {
    const error = {
      title: 'Error',
      message: 'File upload failed',
      guidance: 'Please check your internet connection',
      severity: 'error'
    }
    
    render(<ErrorDisplay error={error} />)
    
    expect(screen.getByText('Suggestion:')).toBeInTheDocument()
    expect(screen.getByText('Please check your internet connection')).toBeInTheDocument()
  })

  test('shows retry button when onRetry provided', () => {
    const mockOnRetry = jest.fn()
    const error = {
      title: 'Error',
      message: 'Failed',
      severity: 'error'
    }
    
    render(<ErrorDisplay error={error} onRetry={mockOnRetry} />)
    
    const retryButton = screen.getByText('Try Again')
    expect(retryButton).toBeInTheDocument()
    
    fireEvent.click(retryButton)
    expect(mockOnRetry).toHaveBeenCalled()
  })

  test('shows dismiss button when onDismiss provided', () => {
    const mockOnDismiss = jest.fn()
    const error = {
      title: 'Error',
      message: 'Failed',
      severity: 'error'
    }
    
    render(<ErrorDisplay error={error} onDismiss={mockOnDismiss} />)
    
    const dismissButton = screen.getByText('Dismiss')
    expect(dismissButton).toBeInTheDocument()
    
    fireEvent.click(dismissButton)
    expect(mockOnDismiss).toHaveBeenCalled()
  })

  test('applies correct styling for error severity', () => {
    const error = {
      title: 'Error',
      message: 'Failed',
      severity: 'error'
    }
    
    const { container } = render(<ErrorDisplay error={error} />)
    expect(container.querySelector('.bg-red-50')).toBeInTheDocument()
  })

  test('applies correct styling for warning severity', () => {
    const error = {
      title: 'Warning',
      message: 'Be careful',
      severity: 'warning'
    }
    
    const { container } = render(<ErrorDisplay error={error} />)
    expect(container.querySelector('.bg-yellow-50')).toBeInTheDocument()
  })

  test('applies correct styling for info severity', () => {
    const error = {
      title: 'Info',
      message: 'Just so you know',
      severity: 'info'
    }
    
    const { container } = render(<ErrorDisplay error={error} />)
    expect(container.querySelector('.bg-blue-50')).toBeInTheDocument()
  })

  test('uses default title when not provided', () => {
    const error = {
      message: 'Something happened',
      severity: 'error'
    }
    
    render(<ErrorDisplay error={error} />)
    expect(screen.getByText('An error occurred')).toBeInTheDocument()
  })
})
