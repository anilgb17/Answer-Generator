import React from 'react'
import { render, screen } from '@testing-library/react'
import ProgressIndicator from '../ProgressIndicator'

describe('ProgressIndicator Component', () => {
  test('renders with default props', () => {
    render(<ProgressIndicator />)
    
    expect(screen.getByText('Processing...')).toBeInTheDocument()
    expect(screen.getByText('0%')).toBeInTheDocument()
  })

  test('displays correct progress percentage', () => {
    render(<ProgressIndicator progress={45} />)
    
    expect(screen.getByText('45%')).toBeInTheDocument()
  })

  test('shows processing status', () => {
    render(<ProgressIndicator status="processing" progress={30} />)
    
    expect(screen.getByText('Processing...')).toBeInTheDocument()
    expect(screen.getByText(/This may take a few moments/i)).toBeInTheDocument()
  })

  test('shows complete status', () => {
    render(<ProgressIndicator status="complete" progress={100} />)
    
    expect(screen.getByText('Complete!')).toBeInTheDocument()
    expect(screen.getByText('100%')).toBeInTheDocument()
  })

  test('shows error status', () => {
    render(<ProgressIndicator status="error" progress={50} />)
    
    expect(screen.getByText('Error')).toBeInTheDocument()
  })

  test('displays custom message', () => {
    const message = 'Generating diagrams...'
    render(<ProgressIndicator message={message} />)
    
    expect(screen.getByText(message)).toBeInTheDocument()
  })

  test('clamps progress to 0-100 range', () => {
    const { rerender } = render(<ProgressIndicator progress={-10} />)
    expect(screen.getByText('-10%')).toBeInTheDocument()
    
    rerender(<ProgressIndicator progress={150} />)
    expect(screen.getByText('150%')).toBeInTheDocument()
  })

  test('applies correct color for processing status', () => {
    const { container } = render(<ProgressIndicator status="processing" progress={50} />)
    const progressBar = container.querySelector('.bg-blue-600')
    expect(progressBar).toBeInTheDocument()
  })

  test('applies correct color for complete status', () => {
    const { container } = render(<ProgressIndicator status="complete" progress={100} />)
    const progressBar = container.querySelector('.bg-green-600')
    expect(progressBar).toBeInTheDocument()
  })

  test('applies correct color for error status', () => {
    const { container } = render(<ProgressIndicator status="error" progress={50} />)
    const progressBar = container.querySelector('.bg-red-600')
    expect(progressBar).toBeInTheDocument()
  })
})
