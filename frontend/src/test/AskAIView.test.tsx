import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AskAIView } from '../components/AskAIView'
import { repoService } from '../services/repoService'

vi.mock('../services/repoService', () => ({
  repoService: {
    ask: vi.fn(),
  },
}))

describe('AskAIView', () => {
  it('renders question input and sample query buttons', () => {
    const onJumpToFile = vi.fn()
    render(<AskAIView repoId="test:repo@123" onJumpToFile={onJumpToFile} />)

    expect(screen.getByPlaceholderText(/where does authentication take place/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ask question/i })).toBeInTheDocument()
    expect(screen.getByText('What does this project do?')).toBeInTheDocument()
  })

  it('submits question and renders answer and verified citations', async () => {
    const onJumpToFile = vi.fn()
    vi.mocked(repoService.ask).mockResolvedValueOnce({
      question: 'Where does the app start?',
      answer: 'The application starts in src/main.py.',
      mode: 'developer',
      provider: 'none (AI-Free Mode)',
      citations: [
        {
          file_path: 'src/main.py',
          start_line: 1,
          end_line: 10,
          repository_revision: '123',
          snippet: 'def main():\n    print("start")',
          github_url: 'https://github.com/test/repo/blob/123/src/main.py#L1-L10',
        },
      ],
      evidence_used: [],
      disclaimer: 'Operating in AI-free mode: Answer generated from verified static code analysis facts.',
    })

    render(<AskAIView repoId="test:repo@123" onJumpToFile={onJumpToFile} />)

    const input = screen.getByPlaceholderText(/where does authentication take place/i)
    fireEvent.change(input, { target: { value: 'Where does the app start?' } })
    fireEvent.click(screen.getByRole('button', { name: /ask question/i }))

    await waitFor(() => {
      expect(screen.getByText(/The application starts in src\/main\.py\./)).toBeInTheDocument()
      expect(screen.getByText('src/main.py')).toBeInTheDocument()
      expect(screen.getByText(/Operating in AI-free mode/)).toBeInTheDocument()
    })

    // Click on citation jump button
    const jumpBtn = screen.getByRole('button', { name: /view in code explorer/i })
    fireEvent.click(jumpBtn)
    expect(onJumpToFile).toHaveBeenCalledWith('src/main.py', 1)
  })

  it('allows clicking sample questions to populate and trigger query', async () => {
    const onJumpToFile = vi.fn()
    vi.mocked(repoService.ask).mockResolvedValueOnce({
      question: 'What does this project do?',
      answer: 'This is a sample project for testing.',
      mode: 'developer',
      provider: 'none',
      citations: [],
      evidence_used: [],
      disclaimer: 'Test disclaimer',
    })

    render(<AskAIView repoId="test:repo@123" onJumpToFile={onJumpToFile} />)

    const sampleBtn = screen.getByText('What does this project do?')
    fireEvent.click(sampleBtn)

    await waitFor(() => {
      expect(repoService.ask).toHaveBeenCalledWith(
        'test:repo@123',
        'What does this project do?',
        'developer'
      )
    })
  })
})
