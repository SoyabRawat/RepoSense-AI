import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { SourceViewer } from '../components/SourceViewer'

describe('SourceViewer', () => {
  it('renders placeholder when no file is selected', () => {
    render(
      <SourceViewer
        path={null}
        content={null}
        isLoading={false}
        error={null}
      />
    )

    expect(screen.getByText(/No File Selected/i)).toBeInTheDocument()
  })

  it('renders line numbers and code content for selected file', () => {
    const code = 'from fastapi import FastAPI\n\napp = FastAPI()\n'
    render(
      <SourceViewer
        path="app/main.py"
        content={code}
        language="Python"
        isLoading={false}
        error={null}
        highlightLine={3}
      />
    )

    expect(screen.getByText('app/main.py')).toBeInTheDocument()
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument() // Line 3
    expect(screen.getByText(/app = FastAPI/)).toBeInTheDocument()
  })

  it('copies content to clipboard on copy button click', () => {
    const code = 'console.log("hello world");'
    const writeTextMock = vi.fn().mockResolvedValue(undefined)
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    })

    render(
      <SourceViewer
        path="index.js"
        content={code}
        language="JavaScript"
        isLoading={false}
        error={null}
      />
    )

    const copyBtn = screen.getByTitle(/Copy source code/i)
    fireEvent.click(copyBtn)

    expect(writeTextMock).toHaveBeenCalledWith(code)
  })

  it('renders empty file placeholder when content is empty string', () => {
    render(
      <SourceViewer
        path="__init__.py"
        content=""
        language="Python"
        isLoading={false}
        error={null}
      />
    )

    expect(screen.getByText(/Empty file/i)).toBeInTheDocument()
    expect(screen.getByText('__init__.py')).toBeInTheDocument()
  })

  it('renders error message when error is provided', () => {
    render(
      <SourceViewer
        path="src/missing.py"
        content={null}
        isLoading={false}
        error="File not found in analyzed repository"
      />
    )

    expect(screen.getByText(/Failed to Load File/i)).toBeInTheDocument()
    expect(screen.getByText(/File not found in analyzed repository/i)).toBeInTheDocument()
  })

  it('safely escapes HTML tags in source code preventing XSS execution', () => {
    const maliciousCode = '<script>alert("xss")</script><img src="x" onerror="evil()">'
    const { container } = render(
      <SourceViewer
        path="sample.html"
        content={maliciousCode}
        language="HTML"
        isLoading={false}
        error={null}
      />
    )

    // Verify no script tags exist in DOM
    const scripts = container.querySelectorAll('script')
    expect(scripts.length).toBe(0)
    // Verify text is safely displayed as text
    expect(screen.getByText(/alert/)).toBeInTheDocument()
  })
})
