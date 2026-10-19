import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { LandingPage } from '../pages/LandingPage'
import { repoService } from '../services/repoService'
import type {
  ArchitectureGraph,
  EntryPointInfo,
  FileContentResponse,
  FileNode,
  LanguageBreakdown,
  RepoMetadata,
} from '../types/repository'

// Mock health check service
vi.mock('../services/api', () => ({
  CONFIGURED_BACKEND_URL: 'http://127.0.0.1:8000',
  getActiveBaseUrl: () => 'http://127.0.0.1:8000',
  checkBackendHealth: vi.fn().mockResolvedValue({
    data: {
      status: 'healthy',
      app_name: 'RepoSense AI Backend',
      version: '0.3.0',
      phase: 'Phase 3 - Testing, Security & Release',
      environment: 'development',
      timestamp: '2026-10-19T10:00:00Z',
      capabilities: {
        health_check: 'active',
        repository_ingestion: 'active',
        ast_static_analysis: 'active',
        full_text_search: 'active',
        ai_explanations: 'active',
      },
    },
    latencyMs: 12,
    endpointUsed: 'http://127.0.0.1:8000/api/v1/health',
  }),
  fetchApi: vi.fn(),
}))

const mockMeta: RepoMetadata = {
  repository_id: 'pallets:flask@abcdef12',
  owner: 'pallets',
  name: 'flask',
  full_name: 'pallets/flask',
  canonical_url: 'https://github.com/pallets/flask',
  default_branch: 'main',
  commit_sha: 'abcdef1234567890',
  description: 'The Python micro framework for building web applications.',
  stars: 68000,
  forks: 16000,
  primary_language: 'Python',
  license: 'BSD-3-Clause',
  file_count: 42,
  total_bytes: 450000,
  analysis_status: 'completed',
}

const mockTree: FileNode = {
  path: '',
  name: 'root',
  type: 'directory',
  size: 0,
  is_supported: true,
  children: [
    {
      path: 'src',
      name: 'src',
      type: 'directory',
      size: 0,
      is_supported: true,
      children: [
        {
          path: 'src/app.py',
          name: 'app.py',
          type: 'file',
          size: 1200,
          language: 'Python',
          is_supported: true,
          is_entry_point: true,
        },
        {
          path: 'src/config.py',
          name: 'config.py',
          type: 'file',
          size: 400,
          language: 'Python',
          is_supported: true,
          is_entry_point: false,
        },
      ],
    },
    {
      path: 'pyproject.toml',
      name: 'pyproject.toml',
      type: 'file',
      size: 800,
      language: 'TOML',
      is_supported: true,
      is_entry_point: false,
    },
  ],
}

const mockLanguages: LanguageBreakdown = {
  languages: { Python: 38, TOML: 2, Markdown: 2 },
  percentages: { Python: 90.5, TOML: 5.0, Markdown: 4.5 },
  byte_counts: { Python: 400000, TOML: 25000, Markdown: 25000 },
  total_supported_files: 42,
  total_repository_files: 45,
}

const mockEntryPoints: EntryPointInfo[] = [
  {
    file_path: 'src/app.py',
    language: 'Python',
    detection_method: 'Flask application factory',
    evidence: "Line 12: app = Flask(__name__)",
    confidence: 'confirmed',
  },
]

const mockGraph: ArchitectureGraph = {
  nodes: [
    {
      id: 'entry:src/app.py',
      label: 'Entry: app.py',
      type: 'entry_point',
      file_path: 'src/app.py',
      language: 'Python',
      metadata: { position: { x: 50, y: 60 } },
    },
    {
      id: 'file:src/config.py',
      label: 'config.py',
      type: 'file',
      file_path: 'src/config.py',
      language: 'Python',
      metadata: { position: { x: 400, y: 60 } },
    },
    {
      id: 'pkg:werkzeug',
      label: 'werkzeug',
      type: 'external_package',
      file_path: null,
      language: 'External',
      metadata: { position: { x: 800, y: 60 } },
    },
  ],
  edges: [
    {
      id: 'e_0',
      source: 'entry:src/app.py',
      target: 'file:src/config.py',
      type: 'imports',
      label: 'imports',
    },
    {
      id: 'e_1',
      source: 'entry:src/app.py',
      target: 'pkg:werkzeug',
      type: 'depends_on',
      label: 'depends on',
    },
  ],
}

const mockFileContent: FileContentResponse = {
  path: 'src/app.py',
  language: 'Python',
  size: 350,
  content: 'from flask import Flask\nfrom config import Config\n\napp = Flask(__name__)\n',
  line_count: 4,
  truncated: false,
}

describe('End-to-End Integration Workflow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(repoService, 'analyzeRepository').mockResolvedValue(mockMeta)
    vi.spyOn(repoService, 'getTree').mockResolvedValue(mockTree)
    vi.spyOn(repoService, 'getLanguages').mockResolvedValue(mockLanguages)
    vi.spyOn(repoService, 'getEntryPoints').mockResolvedValue(mockEntryPoints)
    vi.spyOn(repoService, 'getGraph').mockResolvedValue(mockGraph)
    vi.spyOn(repoService, 'getFileContent').mockResolvedValue(mockFileContent)
    vi.spyOn(repoService, 'search').mockResolvedValue({
      query: 'Flask',
      total_matches: 1,
      results: [
        {
          file_path: 'src/app.py',
          line_number: 1,
          line_content: 'from flask import Flask',
          language: 'Python',
        },
      ],
      is_partial: false,
    })
    vi.spyOn(repoService, 'ask').mockResolvedValue({
      question: 'Where does Flask start?',
      answer: 'The application is initialized in `src/app.py` via `app = Flask(__name__)`.',
      mode: 'developer',
      provider: 'none (AI-Free Mode)',
      citations: [
        {
          file_path: 'src/app.py',
          start_line: 1,
          end_line: 4,
          repository_revision: 'abcdef12',
          snippet: 'app = Flask(__name__)',
          is_valid: true,
        },
      ],
      evidence_used: [],
      disclaimer: 'Operating in AI-free mode: Answer generated from verified static code analysis facts.',
    })
  })

  it('completes the entire repository analysis, exploration, search, and AI Q&A workflow', async () => {
    render(<LandingPage />)

    // 1. Initial Welcome / Landing State
    expect(screen.getByText(/Understand Unfamiliar Codebases/i)).toBeInTheDocument()
    expect(screen.getAllByText(/v0.3.0/i).length).toBeGreaterThan(0)

    // 2. Submit repository URL
    const input = screen.getByPlaceholderText(/Enter public GitHub repo URL/i)
    fireEvent.change(input, { target: { value: 'https://github.com/pallets/flask' } })

    const analyzeBtn = screen.getByRole('button', { name: /Analyze/i })
    await act(async () => {
      fireEvent.click(analyzeBtn)
    })

    // 3. Verify repository is loaded into workspace
    await waitFor(() => {
      expect(screen.getByText('pallets/flask')).toBeInTheDocument()
    })

    expect(screen.getByText(/68,000/)).toBeInTheDocument() // Stars formatted
    expect(screen.getByText('BSD-3-Clause')).toBeInTheDocument()

    // 4. Test Navigation to Code Explorer tab
    const explorerTab = screen.getByRole('button', { name: /Code Explorer/i })
    await act(async () => {
      fireEvent.click(explorerTab)
    })

    await waitFor(() => {
      expect(screen.getByText('Files & Directories')).toBeInTheDocument()
    })

    // 5. Test Navigation to Code Search tab
    const searchTab = screen.getByRole('button', { name: /Code Search/i })
    await act(async () => {
      fireEvent.click(searchTab)
    })

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Search code symbols/i)).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Search code symbols/i)
    fireEvent.change(searchInput, { target: { value: 'Flask' } })

    const submitSearchBtn = screen.getByRole('button', { name: /Search Code/i })
    await act(async () => {
      fireEvent.click(submitSearchBtn)
    })

    await waitFor(() => {
      expect(screen.getByText(/Found/i)).toBeInTheDocument()
      expect(screen.getByText('from flask import Flask')).toBeInTheDocument()
    })

    // 6. Test Navigation to Ask AI tab
    const askTab = screen.getByRole('button', { name: /Ask AI/i })
    await act(async () => {
      fireEvent.click(askTab)
    })

    await waitFor(() => {
      expect(screen.getByText(/Source-Grounded Code Explanations/i)).toBeInTheDocument()
    })

    const askInput = screen.getByPlaceholderText(/Where does authentication take place/i)
    fireEvent.change(askInput, { target: { value: 'Where does Flask start?' } })

    const askBtn = screen.getByRole('button', { name: /Ask Question/i })
    await act(async () => {
      fireEvent.click(askBtn)
    })

    await waitFor(() => {
      expect(screen.getByText(/The application is initialized in/i)).toBeInTheDocument()
      expect(screen.getByText(/Verified Source Citations/i)).toBeInTheDocument()
      expect(screen.getByText('L1-4')).toBeInTheDocument()
    })
  })

  it('handles invalid repository URL submission with clean error display', async () => {
    vi.spyOn(repoService, 'analyzeRepository').mockRejectedValueOnce(
      new Error("Invalid repository host 'evil.com'. Only public 'github.com' repositories are supported.")
    )

    render(<LandingPage />)

    const input = screen.getByPlaceholderText(/Enter public GitHub repo URL/i)
    fireEvent.change(input, { target: { value: 'https://evil.com/fake/repo' } })

    const analyzeBtn = screen.getByRole('button', { name: /Analyze/i })
    await act(async () => {
      fireEvent.click(analyzeBtn)
    })

    await waitFor(() => {
      expect(
        screen.getByText(/Only public 'github.com' repositories are supported/i)
      ).toBeInTheDocument()
    })
  })
})
