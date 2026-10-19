import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { OverviewDashboard } from '../components/OverviewDashboard'
import type { EntryPointInfo, LanguageBreakdown, RepoMetadata } from '../types/repository'

describe('OverviewDashboard', () => {
  const mockMetadata: RepoMetadata = {
    repository_id: 'pallets:flask@abcd1234',
    owner: 'pallets',
    name: 'flask',
    full_name: 'pallets/flask',
    canonical_url: 'https://github.com/pallets/flask',
    default_branch: 'main',
    commit_sha: 'abcd1234567890',
    description: 'The Python micro framework for building web applications.',
    stars: 65000,
    forks: 16000,
    primary_language: 'Python',
    license: 'BSD-3-Clause',
    file_count: 42,
    total_bytes: 150000,
    analysis_timestamp: new Date().toISOString(),
    analysis_status: 'completed',
    status_message: null,
    limits_exceeded: [],
  }

  const mockLanguages: LanguageBreakdown = {
    languages: { Python: 40, HTML: 2 },
    percentages: { Python: 95.2, HTML: 4.8 },
    byte_counts: { Python: 140000, HTML: 10000 },
    total_supported_files: 42,
    total_repository_files: 50,
  }

  const mockEntryPoints: EntryPointInfo[] = [
    {
      file_path: 'src/flask/app.py',
      language: 'Python',
      detection_method: 'WSGI framework factory',
      evidence: 'Line 50: class Flask',
      confidence: 'likely',
    },
  ]

  it('renders repository metadata, stars, forks, and branch', () => {
    render(
      <OverviewDashboard
        metadata={mockMetadata}
        languages={mockLanguages}
        entryPoints={mockEntryPoints}
        onSelectFile={vi.fn()}
      />
    )

    expect(screen.getByText('pallets/flask')).toBeInTheDocument()
    expect(screen.getByText(/65,000 stars/i)).toBeInTheDocument()
    expect(screen.getByText(/16,000 forks/i)).toBeInTheDocument()
    expect(screen.getByText('main')).toBeInTheDocument()
    expect(screen.getByText('BSD-3-Clause')).toBeInTheDocument()
  })

  it('renders programming language percentages and entry points', () => {
    const onSelectFile = vi.fn()
    render(
      <OverviewDashboard
        metadata={mockMetadata}
        languages={mockLanguages}
        entryPoints={mockEntryPoints}
        onSelectFile={onSelectFile}
      />
    )

    expect(screen.getByText('95.2%')).toBeInTheDocument()
    expect(screen.getByText('src/flask/app.py')).toBeInTheDocument()

    // Clicking entry point triggers onSelectFile
    const epCard = screen.getByText('src/flask/app.py').closest('div')
    if (epCard) {
      fireEvent.click(epCard)
      expect(onSelectFile).toHaveBeenCalledWith('src/flask/app.py')
    }
  })
})
