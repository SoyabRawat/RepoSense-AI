import React, { useState } from 'react'
import {
  Search,
  FileCode,
  ArrowRight,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { repoService } from '../services/repoService'
import type { SearchResponse } from '../types/repository'

interface CodeSearchViewProps {
  repoId: string
  onJumpToFile: (path: string, line: number) => void
}

export const CodeSearchView: React.FC<CodeSearchViewProps> = ({
  repoId,
  onJumpToFile,
}) => {
  const [query, setQuery] = useState('')
  const [caseSensitive, setCaseSensitive] = useState(false)
  const [pathFilter, setPathFilter] = useState('')
  const [langFilter, setLangFilter] = useState('')

  const [isLoading, setIsLoading] = useState(false)
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)
    try {
      const resp = await repoService.search(
        repoId,
        query.trim(),
        caseSensitive,
        pathFilter.trim() || undefined,
        langFilter.trim() || undefined
      )
      setSearchResponse(resp)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Search Header Controls */}
      <form
        onSubmit={handleSearch}
        className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4"
      >
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search code symbols, functions, keywords, or text..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/30 font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-md shadow-indigo-600/30 transition-all shrink-0"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Search Code</span>
              </>
            )}
          </button>
        </div>

        {/* Filters Row */}
        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={caseSensitive}
              onChange={(e) => setCaseSensitive(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0 focus:ring-offset-0"
            />
            <span>Case Sensitive</span>
          </label>

          <div className="flex items-center gap-1.5">
            <span>Path filter:</span>
            <input
              type="text"
              value={pathFilter}
              onChange={(e) => setPathFilter(e.target.value)}
              placeholder="e.g. src/ or api/"
              className="px-2 py-1 rounded bg-slate-950 border border-slate-800 text-slate-200 text-xs w-32 focus:outline-none focus:border-indigo-500/60"
            />
          </div>

          <div className="flex items-center gap-1.5">
            <span>Language:</span>
            <input
              type="text"
              value={langFilter}
              onChange={(e) => setLangFilter(e.target.value)}
              placeholder="e.g. Python, TS"
              className="px-2 py-1 rounded bg-slate-950 border border-slate-800 text-slate-200 text-xs w-32 focus:outline-none focus:border-indigo-500/60"
            />
          </div>
        </div>
      </form>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 flex items-start gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Results List */}
      {searchResponse && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span>
              Found <strong className="text-white">{searchResponse.total_matches}</strong> matches for{' '}
              <code className="text-indigo-400 font-mono">"{searchResponse.query}"</code>
            </span>
            {searchResponse.is_partial && (
              <span className="text-amber-400">
                (Results capped at {searchResponse.results.length} matches)
              </span>
            )}
          </div>

          {searchResponse.results.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500 rounded-2xl bg-slate-900/40 border border-slate-800">
              No matches found across the analyzed repository files.
            </div>
          ) : (
            <div className="space-y-3">
              {searchResponse.results.map((result, idx) => (
                <div
                  key={`${result.file_path}-${result.line_number}-${idx}`}
                  onClick={() => onJumpToFile(result.file_path, result.line_number)}
                  className="p-4 rounded-xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition-all duration-200 cursor-pointer group space-y-2 shadow-md"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-indigo-400" />
                      <span className="font-mono text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                        {result.file_path}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40">
                        Line {result.line_number}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-xs text-slate-500 group-hover:text-indigo-400 transition-colors">
                      <span>Jump to line</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </div>

                  {/* Context Snippet */}
                  <div className="p-2.5 rounded-lg bg-slate-950 font-mono text-xs text-slate-300 overflow-x-auto space-y-0.5">
                    {result.context_before?.map((ctxLine, i) => (
                      <div key={i} className="text-slate-600 truncate">
                        {ctxLine}
                      </div>
                    ))}
                    <div className="bg-indigo-500/20 text-indigo-200 font-semibold px-1 py-0.5 rounded -mx-1">
                      {result.line_content}
                    </div>
                    {result.context_after?.map((ctxLine, i) => (
                      <div key={i} className="text-slate-600 truncate">
                        {ctxLine}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
