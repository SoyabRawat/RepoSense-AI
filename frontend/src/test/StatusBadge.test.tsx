import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusBadge } from '../components/StatusBadge'

describe('StatusBadge', () => {
  it('renders loading state correctly', () => {
    render(<StatusBadge status="loading" />)
    expect(screen.getByText(/Checking Connection/i)).toBeInTheDocument()
  })

  it('renders connected state with latency', () => {
    render(<StatusBadge status="connected" latencyMs={12} />)
    expect(screen.getByText(/API Online \(12ms\)/i)).toBeInTheDocument()
  })

  it('renders disconnected state on error', () => {
    render(<StatusBadge status="error" />)
    expect(screen.getByText(/API Disconnected/i)).toBeInTheDocument()
  })
})
