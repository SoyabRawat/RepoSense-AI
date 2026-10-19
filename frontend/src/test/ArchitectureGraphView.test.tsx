import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ArchitectureGraphView } from '../components/ArchitectureGraphView'
import type { ArchitectureGraph } from '../types/repository'

// Mock @xyflow/react for jsdom
vi.mock('@xyflow/react', () => ({
  ReactFlow: ({ children, nodes }: { children: React.ReactNode; nodes: Array<{ id: string; data: { label: React.ReactNode } }> }) => (
    <div data-testid="mock-reactflow">
      {nodes.map((n) => (
        <div key={n.id} data-testid={`node-${n.id}`}>
          {n.data.label}
        </div>
      ))}
      {children}
    </div>
  ),
  Controls: () => <div data-testid="mock-controls" />,
  Background: () => <div data-testid="mock-background" />,
  BackgroundVariant: { Dots: 'dots' },
  Panel: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  MarkerType: { ArrowClosed: 'arrowclosed' },
}))

const mockGraph: ArchitectureGraph = {
  nodes: [
    {
      id: 'src/main.py',
      label: 'src/main.py',
      type: 'entry_point',
      metadata: { path: 'src/main.py', language: 'Python', position: { x: 50, y: 50 } },
    },
    {
      id: 'src/utils.py',
      label: 'src/utils.py',
      type: 'file',
      metadata: { path: 'src/utils.py', language: 'Python', position: { x: 250, y: 50 } },
    },
    {
      id: 'pkg:flask',
      label: 'flask',
      type: 'external_package',
      metadata: { position: { x: 450, y: 50 } },
    },
  ],
  edges: [
    {
      source: 'src/main.py',
      target: 'src/utils.py',
      type: 'imports',
    },
    {
      source: 'src/main.py',
      target: 'pkg:flask',
      type: 'declares_dependency',
    },
  ],
  entry_points: ['src/main.py'],
  total_modules: 2,
  total_dependencies: 2,
}

describe('ArchitectureGraphView', () => {
  it('renders graph nodes, statistics, and controls', () => {
    const onSelectFile = vi.fn()
    render(<ArchitectureGraphView graph={mockGraph} onSelectFile={onSelectFile} />)

    expect(screen.getByTestId('node-src/main.py')).toBeInTheDocument()
    expect(screen.getByTestId('node-src/utils.py')).toBeInTheDocument()
    expect(screen.getByTestId('node-pkg:flask')).toBeInTheDocument()
    expect(screen.getByText(/3 nodes/i)).toBeInTheDocument()
    expect(screen.getByText(/2 edges/i)).toBeInTheDocument()
  })

  it('filters nodes based on type selector button', () => {
    const onSelectFile = vi.fn()
    render(<ArchitectureGraphView graph={mockGraph} onSelectFile={onSelectFile} />)

    const entryBtn = screen.getByRole('button', { name: 'Entry Points' })
    fireEvent.click(entryBtn)

    expect(screen.getByTestId('node-src/main.py')).toBeInTheDocument()
    expect(screen.queryByTestId('node-pkg:flask')).not.toBeInTheDocument()
  })

  it('filters nodes based on search query', () => {
    const onSelectFile = vi.fn()
    render(<ArchitectureGraphView graph={mockGraph} onSelectFile={onSelectFile} />)

    const searchInput = screen.getByPlaceholderText(/find node/i)
    fireEvent.change(searchInput, { target: { value: 'utils' } })

    expect(screen.getByTestId('node-src/utils.py')).toBeInTheDocument()
    expect(screen.queryByTestId('node-pkg:flask')).not.toBeInTheDocument()
  })

  it('renders empty placeholder if graph is null or empty', () => {
    const onSelectFile = vi.fn()
    render(<ArchitectureGraphView graph={null} onSelectFile={onSelectFile} />)

    expect(screen.getByText(/no relationships found/i)).toBeInTheDocument()
  })
})
