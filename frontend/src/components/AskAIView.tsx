import React, { useState } from 'react'
import {
  Sparkles,
  Send,
  Loader2,
  FileCode,
  ExternalLink,
  ArrowRight,
  ShieldCheck,
  HelpCircle,
  Code2,
} from 'lucide-react'
import { repoService } from '../services/repoService'
import type { AskResponse } from '../types/repository'

interface AskAIViewProps {
  repoId: string
  onJumpToFile: (path: string, line: number) => void
}

const SAMPLE_QUESTIONS = [
  'What does this project do?',
  'Where does the application start?',
  'How are module relationships structured?',
  'Explain the main entry point and configuration',
]

export const AskAIView: React.FC<AskAIViewProps> = ({ repoId, onJumpToFile }) => {
  const [question, setQuestion] = useState('')
  const [mode, setMode] = useState<'beginner' | 'developer'>('developer')

  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<AskResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAsk = async (queryToAsk?: string) => {
    const q = (queryToAsk || question).trim()
    if (!q) return

    setIsLoading(true)
    setError(null)
    try {
      const res = await repoService.ask(repoId, q, mode)
      setResponse(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Question Form & Mode Switcher */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        {/* Mode Selector */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div className="space-y-0.5">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              Source-Grounded Code Explanations
            </h3>
            <p className="text-xs text-slate-400">
              Ask questions backed by verified static analysis evidence and source file citations.
            </p>
          </div>

          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-950 border border-slate-800 shrink-0">
            <button
              type="button"
              onClick={() => setMode('beginner')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                mode === 'beginner'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Beginner Mode</span>
            </button>
            <button
              type="button"
              onClick={() => setMode('developer')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                mode === 'developer'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Developer Mode</span>
            </button>
          </div>
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleAsk()
          }}
          className="flex flex-col sm:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., Where does authentication take place? What does this project do?"
              disabled={isLoading}
              className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/30"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !question.trim()}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-md shadow-indigo-600/30 transition-all shrink-0"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Explaining...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Ask Question</span>
              </>
            )}
          </button>
        </form>

        {/* Prompt Suggestions */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-slate-500">Suggestions:</span>
          {SAMPLE_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              disabled={isLoading}
              onClick={() => {
                setQuestion(q)
                handleAsk(q)
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/40 text-slate-300 hover:text-white transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Answer Section */}
      {response && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-2xl space-y-6">
          {/* Answer Metadata Ribbon */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800/80 text-xs">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-lg bg-indigo-950/80 text-indigo-300 border border-indigo-800/50 font-medium">
                Provider: {response.provider}
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
                Mode: {response.mode}
              </span>
            </div>

            {response.disclaimer && (
              <span className="text-[11px] text-slate-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                {response.disclaimer}
              </span>
            )}
          </div>

          {/* Formatted Answer Body */}
          <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-line space-y-3 font-sans">
            {response.answer}
          </div>

          {/* Source Citations Section */}
          {response.citations.length > 0 && (
            <div className="pt-4 border-t border-slate-800/80 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <FileCode className="w-4 h-4 text-indigo-400" />
                  Verified Source Citations ({response.citations.length})
                </h4>
                <span className="text-[11px] text-emerald-400 font-medium">
                  &check; Validated against repository revision
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {response.citations.map((citation, idx) => (
                  <div
                    key={`${citation.file_path}-${citation.start_line}-${idx}`}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-indigo-500/40 transition-colors space-y-2 group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 truncate">
                        <FileCode className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                        <span className="font-mono text-xs font-semibold text-slate-200 truncate">
                          {citation.file_path}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-indigo-300 shrink-0">
                        L{citation.start_line}-{citation.end_line}
                      </span>
                    </div>

                    {citation.snippet && (
                      <div className="p-2 rounded bg-slate-900 font-mono text-[11px] text-slate-300 max-h-24 overflow-hidden text-ellipsis whitespace-pre">
                        {citation.snippet}
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-1">
                      <button
                        type="button"
                        onClick={() => onJumpToFile(citation.file_path, citation.start_line)}
                        className="flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
                      >
                        <span>View in Code Explorer</span>
                        <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                      </button>

                      {citation.github_url && (
                        <a
                          href={citation.github_url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1 text-slate-500 hover:text-slate-300 transition-colors"
                          title="View on GitHub"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
