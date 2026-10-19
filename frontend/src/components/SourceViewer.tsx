import React, { useEffect, useRef, useState, useMemo } from 'react'
import {
  Copy,
  Check,
  ExternalLink,
  FileCode,
  AlertCircle,
  Loader2,
} from 'lucide-react'
import hljs from 'highlight.js'

interface SourceViewerProps {
  path: string | null
  content: string | null
  language?: string | null
  isLoading: boolean
  error: string | null
  highlightLine?: number | null
  commitSha?: string
  canonicalUrl?: string
}

export const SourceViewer: React.FC<SourceViewerProps> = ({
  path,
  content,
  language,
  isLoading,
  error,
  highlightLine,
  commitSha,
  canonicalUrl,
}) => {
  const [copied, setCopied] = useState(false)
  const lineRefs = useRef<{ [key: number]: HTMLDivElement | null }>({})

  // Auto-scroll to highlighted line if specified
  useEffect(() => {
    if (highlightLine && lineRefs.current[highlightLine]) {
      const el = lineRefs.current[highlightLine]
      if (typeof el?.scrollIntoView === 'function') {
        el.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        })
      }
    }
  }, [highlightLine, content])

  const handleCopy = () => {
    if (content) {
      navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // Pre-split lines and syntax highlight
  const lines = useMemo(() => {
    if (!content) return []
    return content.split('\n')
  }, [content])

  // Compute highlighted code
  const highlightedLines = useMemo(() => {
    if (!content) return []
    try {
      const detectedLang = language ? language.toLowerCase() : undefined
      const validLang = detectedLang && hljs.getLanguage(detectedLang) ? detectedLang : undefined
      const highlighted = validLang
        ? hljs.highlight(content, { language: validLang }).value
        : hljs.highlightAuto(content).value

      return highlighted.split('\n')
    } catch {
      // Fallback to text escaping
      return lines.map((l) =>
        l.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      )
    }
  }, [content, language, lines])

  if (!path) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] p-8 text-center bg-slate-950/80 border border-slate-800 rounded-2xl shadow-lg">
        <FileCode className="w-12 h-12 text-slate-700 mb-3" />
        <h4 className="text-base font-semibold text-slate-300">No File Selected</h4>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          Select any file from the file explorer on the left or an entry point to inspect its source code.
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] p-8 bg-slate-950/80 border border-slate-800 rounded-2xl shadow-lg">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mb-3" />
        <span className="text-xs text-slate-400 font-mono">Loading {path}...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] p-8 text-center bg-slate-950/80 border border-slate-800 rounded-2xl shadow-lg text-rose-300 space-y-2">
        <AlertCircle className="w-10 h-10 text-rose-400" />
        <h4 className="text-sm font-semibold">Failed to Load File</h4>
        <p className="text-xs text-rose-200/80 max-w-sm">{error}</p>
      </div>
    )
  }

  const githubFileUrl =
    canonicalUrl && commitSha
      ? `${canonicalUrl}/blob/${commitSha}/${path}${highlightLine ? `#L${highlightLine}` : ''}`
      : undefined

  return (
    <div className="flex flex-col h-full bg-slate-950/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      {/* Sticky Top Header */}
      <div className="px-4 py-3 border-b border-slate-800/80 bg-slate-900/90 backdrop-blur-md flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 truncate">
          <FileCode className="w-4 h-4 text-indigo-400 shrink-0" />
          <span className="font-mono text-xs font-semibold text-slate-200 truncate">
            {path}
          </span>
          {language && (
            <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] text-indigo-300 font-medium">
              {language}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[11px] text-slate-500 font-mono">
            {lines.length} lines &bull; {content ? (new Blob([content]).size / 1024).toFixed(1) : 0} KB
          </span>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-xs text-slate-300 hover:text-white transition-colors"
            title="Copy source code"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[10px] text-emerald-400 font-medium">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span className="text-[10px]">Copy</span>
              </>
            )}
          </button>

          {githubFileUrl && (
            <a
              href={githubFileUrl}
              target="_blank"
              rel="noreferrer"
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-slate-400 hover:text-white transition-colors"
              title="Open file on GitHub"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>

      {/* Code Area with Line Numbers */}
      <div className="flex-1 overflow-auto font-mono text-xs text-slate-200 p-4">
        {lines.length === 0 ? (
          <div className="text-slate-500 text-center py-12">Empty file</div>
        ) : (
          <div className="min-w-full inline-block">
            {highlightedLines.map((lineHtml, idx) => {
              const lineNo = idx + 1
              const isHighlighted = highlightLine === lineNo

              return (
                <div
                  key={lineNo}
                  ref={(el) => {
                    lineRefs.current[lineNo] = el
                  }}
                  className={`flex leading-relaxed group transition-colors duration-150 ${
                    isHighlighted
                      ? 'bg-amber-500/15 border-l-2 border-amber-400 -ml-4 pl-4'
                      : 'hover:bg-slate-900/60'
                  }`}
                >
                  {/* Line Number */}
                  <span
                    className={`w-12 text-right pr-4 select-none shrink-0 ${
                      isHighlighted ? 'text-amber-400 font-bold' : 'text-slate-600 group-hover:text-slate-400'
                    }`}
                  >
                    {lineNo}
                  </span>

                  {/* Code Line */}
                  <span
                    className="flex-1 whitespace-pre pr-4"
                    dangerouslySetInnerHTML={{ __html: lineHtml || '&nbsp;' }}
                  />
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
