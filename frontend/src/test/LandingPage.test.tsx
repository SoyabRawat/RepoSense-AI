import { describe, it, expect, vi } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { LandingPage } from '../pages/LandingPage'

vi.mock('../services/api', () => ({
  BACKEND_URL: 'http://127.0.0.1:8000',
  checkBackendHealth: vi.fn().mockResolvedValue({
    data: {
      status: 'healthy',
      app_name: 'RepoSense AI Backend',
      version: '0.1.0-alpha.1',
      phase: 'Phase 1 - Foundation & Architecture',
      environment: 'development',
      timestamp: '2026-10-15T12:00:00Z',
      capabilities: {
        health_check: 'active',
        repository_ingestion: 'unimplemented (planned for Phase 2)',
      },
    },
    latencyMs: 15,
  }),
}))

describe('LandingPage', () => {
  it('renders application title and phase badge', async () => {
    await act(async () => {
      render(<LandingPage />)
    })
    expect(screen.getByText(/Understand Unfamiliar Codebases/i)).toBeInTheDocument()
    const phaseElements = screen.getAllByText(/Phase 1: Foundation/i)
    expect(phaseElements.length).toBeGreaterThan(0)
  })

  it('renders the 3-phase roadmap progression', async () => {
    await act(async () => {
      render(<LandingPage />)
    })
    expect(screen.getByText(/Phase 1: Foundation & Arch/i)).toBeInTheDocument()
    expect(screen.getByText(/Phase 2: Core Development/i)).toBeInTheDocument()
    expect(screen.getByText(/Phase 3: Testing & Release/i)).toBeInTheDocument()
  })

  it('renders architecture specifications card', async () => {
    await act(async () => {
      render(<LandingPage />)
    })
    expect(screen.getByText(/System Architecture & Specs/i)).toBeInTheDocument()
  })
})
