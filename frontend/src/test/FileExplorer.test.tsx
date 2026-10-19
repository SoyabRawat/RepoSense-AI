import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FileExplorer } from '../components/FileExplorer'
import type { FileNode } from '../types/repository'

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
          path: 'src/main.py',
          name: 'main.py',
          type: 'file',
          size: 120,
          language: 'Python',
          is_supported: true,
          is_entry_point: true,
        },
        {
          path: 'src/utils.py',
          name: 'utils.py',
          type: 'file',
          size: 80,
          language: 'Python',
          is_supported: true,
          is_entry_point: false,
        },
      ],
    },
    {
      path: 'README.md',
      name: 'README.md',
      type: 'file',
      size: 500,
      language: 'Markdown',
      is_supported: true,
      is_entry_point: false,
    },
  ],
}

describe('FileExplorer', () => {
  it('renders directory hierarchy and files', () => {
    const onSelectFile = vi.fn()
    render(
      <FileExplorer
        tree={mockTree}
        selectedPath="src/main.py"
        onSelectFile={onSelectFile}
      />
    )

    expect(screen.getByText('Files & Directories')).toBeInTheDocument()
    expect(screen.getByText('README.md')).toBeInTheDocument()
    expect(screen.getByText('src')).toBeInTheDocument()
    expect(screen.getByText('main.py')).toBeInTheDocument()
  })

  it('calls onSelectFile when a file is clicked', () => {
    const onSelectFile = vi.fn()
    render(
      <FileExplorer
        tree={mockTree}
        selectedPath={null}
        onSelectFile={onSelectFile}
      />
    )

    const readmeNode = screen.getByText('README.md')
    fireEvent.click(readmeNode)
    expect(onSelectFile).toHaveBeenCalledWith('README.md')
  })

  it('filters file list when query is entered', () => {
    const onSelectFile = vi.fn()
    render(
      <FileExplorer
        tree={mockTree}
        selectedPath={null}
        onSelectFile={onSelectFile}
      />
    )

    const filterInput = screen.getByPlaceholderText(/filter files/i)
    fireEvent.change(filterInput, { target: { value: 'utils' } })

    expect(screen.getByText('utils.py')).toBeInTheDocument()
    expect(screen.queryByText('README.md')).not.toBeInTheDocument()
  })
})
