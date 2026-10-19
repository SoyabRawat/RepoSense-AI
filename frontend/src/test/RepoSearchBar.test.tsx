import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { RepoSearchBar } from '../components/RepoSearchBar'

describe('RepoSearchBar', () => {
  it('renders input field, analyze button, and sample presets', () => {
    render(
      <RepoSearchBar
        onAnalyze={vi.fn()}
        isLoading={false}
        error={null}
        activeStep={0}
      />
    )

    expect(screen.getByPlaceholderText(/Enter public GitHub repo URL/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Analyze Repo/i })).toBeInTheDocument()
    expect(screen.getByText('Flask')).toBeInTheDocument()
    expect(screen.getByText('FastAPI')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
  })

  it('triggers onAnalyze when submitting a valid repository URL', () => {
    const onAnalyze = vi.fn()
    render(
      <RepoSearchBar
        onAnalyze={onAnalyze}
        isLoading={false}
        error={null}
        activeStep={0}
      />
    )

    const input = screen.getByPlaceholderText(/Enter public GitHub repo URL/i)
    fireEvent.change(input, { target: { value: 'https://github.com/pallets/flask' } })

    const button = screen.getByRole('button', { name: /Analyze Repo/i })
    fireEvent.click(button)

    expect(onAnalyze).toHaveBeenCalledWith('https://github.com/pallets/flask')
  })

  it('displays active step progress when isLoading is true', () => {
    render(
      <RepoSearchBar
        onAnalyze={vi.fn()}
        isLoading={true}
        error={null}
        activeStep={2}
      />
    )

    expect(screen.getByText(/Repository Analysis in Progress/i)).toBeInTheDocument()
    expect(screen.getByText(/Reading repository file tree/i)).toBeInTheDocument()
  })

  it('displays error message and actionable recovery tip when error is provided', () => {
    render(
      <RepoSearchBar
        onAnalyze={vi.fn()}
        isLoading={false}
        error="GitHub API rate limit exceeded. Provide a GITHUB_TOKEN for higher rate limits."
        activeStep={0}
      />
    )

    expect(screen.getByText(/Repository Analysis Failed/i)).toBeInTheDocument()
    expect(screen.getByText(/Recovery Tip:/i)).toBeInTheDocument()
    expect(screen.getByText(/Add a GITHUB_TOKEN to backend\/\.env/i)).toBeInTheDocument()
  })
})
