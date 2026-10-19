import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { CodeSearchView } from '../components/CodeSearchView'
import { repoService } from '../services/repoService'

vi.mock('../services/repoService', () => ({
  repoService: {
    search: vi.fn(),
  },
}))

describe('CodeSearchView', () => {
  it('renders search form input controls', () => {
    const onJumpToFile = vi.fn()
    render(<CodeSearchView repoId="test:repo@123" onJumpToFile={onJumpToFile} />)

    expect(screen.getByPlaceholderText(/search code symbols/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /search code/i })).toBeInTheDocument()
    expect(screen.getByText(/case sensitive/i)).toBeInTheDocument()
  })

  it('executes search query and displays result matches', async () => {
    const onJumpToFile = vi.fn()
    vi.mocked(repoService.search).mockResolvedValueOnce({
      query: 'def calculate',
      total_matches: 1,
      is_partial: false,
      results: [
        {
          file_path: 'src/calc.py',
          line_number: 12,
          line_content: 'def calculate(x, y):',
          context_before: ['# helper module'],
          context_after: ['    return x + y'],
          language: 'Python',
        },
      ],
    })

    render(<CodeSearchView repoId="test:repo@123" onJumpToFile={onJumpToFile} />)

    const input = screen.getByPlaceholderText(/search code symbols/i)
    fireEvent.change(input, { target: { value: 'def calculate' } })
    fireEvent.click(screen.getByRole('button', { name: /search code/i }))

    await waitFor(() => {
      expect(screen.getByText('src/calc.py')).toBeInTheDocument()
      expect(screen.getByText('def calculate(x, y):')).toBeInTheDocument()
      expect(screen.getByText(/Line 12/i)).toBeInTheDocument()
    })

    const jumpButton = screen.getByText(/jump to line/i)
    fireEvent.click(jumpButton)
    expect(onJumpToFile).toHaveBeenCalledWith('src/calc.py', 12)
  })

  it('displays empty state when no matches found', async () => {
    const onJumpToFile = vi.fn()
    vi.mocked(repoService.search).mockResolvedValueOnce({
      query: 'nonexistent_symbol',
      total_matches: 0,
      is_partial: false,
      results: [],
    })

    render(<CodeSearchView repoId="test:repo@123" onJumpToFile={onJumpToFile} />)

    const input = screen.getByPlaceholderText(/search code symbols/i)
    fireEvent.change(input, { target: { value: 'nonexistent_symbol' } })
    fireEvent.click(screen.getByRole('button', { name: /search code/i }))

    await waitFor(() => {
      expect(screen.getByText(/no matches found/i)).toBeInTheDocument()
    })
  })
})
