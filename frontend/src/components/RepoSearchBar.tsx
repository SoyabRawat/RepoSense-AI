import React, { useState } from 'react'
import { Search, Loader2, Sparkles, CheckCircle2, AlertCircle, GitBranch } from 'lucide-react'

interface RepoSearchBarProps {
  onAnalyze: (url: string) => Promise<void>
  isLoading: boolean
  error: string | null
  activeStep: number
}

const PRESET_REPOS = [
  { label: 'Flask', url: 'https://github.com/pallets/flask', lang: 'Python' },
  { label: 'FastAPI', url: 'https://github.com/fastapi/fastapi', lang: 'Python' },
  { label: 'React', url: 'https://github.com/facebook/react', lang: 'TypeScript' },
  { label: 'Express', url: 'https://github.com/expressjs/express', lang: 'JavaScript' },
]

const PROGRESS_STEPS = [
  'Validating repository URL & SSRF check',
  'Retrieving repository metadata & commit revision',
  'Reading repository file tree',
  'Processing supported source files & manifests',
  'Analyzing static imports & code relationships',
  'Preparing architecture graph & search index',
]

export const RepoSearchBar: React.FC<RepoSearchBarProps> = ({
  onAnalyze,
  isLoading,
  error,
  activeStep,
}) => {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim() && !isLoading) {
      onAnalyze(url.trim())
    }
  }

  const handleSelectPreset = (presetUrl: string) => {
    setUrl(presetUrl)
    if (!isLoading) {
      onAnalyze(presetUrl)
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Search Input Bar */}
      <form onSubmit={handleSubmit} className="relative group">
        <div className="relative flex items-center rounded-2xl bg-slate-900/90 border border-slate-700/80 shadow-2xl shadow-indigo-950/40 backdrop-blur-xl transition-all duration-300 focus-within:border-indigo-500/80 focus-within:ring-2 focus-within:ring-indigo-500/30">
          <div className="pl-4 text-slate-400 flex items-center pointer-events-none">
            <GitBranch className="w-5 h-5 text-indigo-400" />
          </div>

          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter public GitHub repo URL (e.g., https://github.com/pallets/flask)"
            disabled={isLoading}
            className="w-full bg-transparent px-3.5 py-4 text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none disabled:opacity-50 font-mono"
            required
          />

          <div className="pr-3 flex items-center gap-2">
            <button
              type="submit"
              disabled={isLoading || !url.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-indigo-600/30 hover:shadow-indigo-500/40 transition-all duration-200"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-indigo-200" />
                  <span>Analyze Repo</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Quick Presets */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-400 flex items-center gap-1 font-medium">
          <Search className="w-3.5 h-3.5 text-slate-400" />
          Quick Samples:
        </span>
        {PRESET_REPOS.map((preset) => (
          <button
            key={preset.url}
            type="button"
            disabled={isLoading}
            onClick={() => handleSelectPreset(preset.url)}
            className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-indigo-500/50 hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            <span className="font-medium">{preset.label}</span>
            <span className="ml-1 text-[10px] text-indigo-400">({preset.lang})</span>
          </button>
        ))}
      </div>

      {/* Progress Box during Analysis */}
      {isLoading && (
        <div className="p-4 rounded-xl bg-slate-900/95 border border-indigo-500/30 shadow-xl space-y-3">
          <div className="flex items-center justify-between text-xs text-indigo-300">
            <span className="font-semibold flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
              Repository Analysis in Progress
            </span>
            <span className="font-mono text-slate-400">
              Step {Math.min(activeStep + 1, PROGRESS_STEPS.length)} of {PROGRESS_STEPS.length}
            </span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 h-1.5 transition-all duration-500 rounded-full"
              style={{
                width: `${((Math.min(activeStep + 1, PROGRESS_STEPS.length)) / PROGRESS_STEPS.length) * 100}%`,
              }}
            />
          </div>

          <div className="space-y-1 pt-1">
            {PROGRESS_STEPS.map((step, idx) => {
              const isDone = idx < activeStep
              const isCurrent = idx === activeStep
              return (
                <div
                  key={step}
                  className={`flex items-center gap-2 text-xs transition-opacity duration-200 ${
                    isDone
                      ? 'text-emerald-400 font-medium'
                      : isCurrent
                      ? 'text-indigo-300 font-semibold'
                      : 'text-slate-600'
                  }`}
                >
                  {isDone ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin shrink-0" />
                  ) : (
                    <div className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0" />
                  )}
                  <span>{step}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Error Banner with Actionable Recovery Guidance */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 flex items-start gap-3 text-rose-200 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1.5 flex-1">
            <p className="font-semibold text-rose-300">Repository Analysis Failed</p>
            <p className="text-xs text-rose-200/90 leading-relaxed font-mono bg-rose-950/50 p-2 rounded-lg border border-rose-900/50">
              {error}
            </p>
            <div className="text-xs text-slate-300 pt-1 flex items-center gap-1.5">
              <span className="font-medium text-amber-300">Recovery Tip:</span>
              <span>
                {error.toLowerCase().includes('rate limit')
                  ? 'Add a GITHUB_TOKEN to backend/.env to increase rate limits to 5,000 req/hr.'
                  : error.toLowerCase().includes('not found') || error.toLowerCase().includes('404')
                  ? 'Ensure the repository exists, is public, and the URL spelling is correct.'
                  : error.toLowerCase().includes('time') || error.toLowerCase().includes('network')
                  ? 'Network request timed out. Verify your connection and retry.'
                  : error.toLowerCase().includes('host') || error.toLowerCase().includes('scheme')
                  ? 'Enter a valid public GitHub repository URL, e.g. https://github.com/pallets/flask.'
                  : 'Check backend status, ensure port 8000 is running, and try again.'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
