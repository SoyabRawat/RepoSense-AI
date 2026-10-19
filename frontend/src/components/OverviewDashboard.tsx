import React from 'react'
import {
  Star,
  GitFork,
  GitBranch,
  FileCode2,
  Scale,
  ExternalLink,
  ShieldAlert,
  CheckCircle2,
  Sparkles,
  ArrowRight,
} from 'lucide-react'
import type { EntryPointInfo, LanguageBreakdown, RepoMetadata } from '../types/repository'

interface OverviewDashboardProps {
  metadata: RepoMetadata
  languages: LanguageBreakdown | null
  entryPoints: EntryPointInfo[]
  onSelectFile: (path: string) => void
}

const LANGUAGE_COLORS: Record<string, string> = {
  Python: '#3572A5',
  TypeScript: '#3178C6',
  JavaScript: '#F1E05A',
  Java: '#B07219',
  'C++': '#F34B7D',
  C: '#555555',
  Go: '#00ADD8',
  Rust: '#DEA584',
  HTML: '#E34C26',
  CSS: '#563D7C',
  Markdown: '#083fa1',
  JSON: '#292929',
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  metadata,
  languages,
  entryPoints,
  onSelectFile,
}) => {
  return (
    <div className="space-y-6">
      {/* Top Banner: Repo Title & GitHub Stats */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-white tracking-tight">
                {metadata.full_name}
              </h2>
              <a
                href={metadata.canonical_url}
                target="_blank"
                rel="noreferrer"
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                title="View on GitHub"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
            {metadata.description && (
              <p className="text-slate-400 text-sm max-w-3xl leading-relaxed">
                {metadata.description}
              </p>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-medium text-amber-300">
              <Star className="w-3.5 h-3.5 fill-amber-400/20 text-amber-400" />
              {metadata.stars.toLocaleString()} stars
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-medium text-slate-300">
              <GitFork className="w-3.5 h-3.5 text-slate-400" />
              {metadata.forks.toLocaleString()} forks
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-medium text-indigo-300">
              <GitBranch className="w-3.5 h-3.5 text-indigo-400" />
              {metadata.default_branch}
            </span>
            {metadata.license && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-medium text-slate-300">
                <Scale className="w-3.5 h-3.5 text-slate-400" />
                {metadata.license}
              </span>
            )}
          </div>
        </div>

        {/* Revision & Status Ribbon */}
        <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
          <div className="flex items-center gap-3">
            <span>
              Analyzed Revision:{' '}
              <code className="text-indigo-400 font-mono bg-indigo-950/40 px-1.5 py-0.5 rounded border border-indigo-800/50">
                {metadata.commit_sha.slice(0, 10)}
              </code>
            </span>
            <span>&bull;</span>
            <span>{metadata.file_count} files analyzed</span>
            <span>&bull;</span>
            <span>{(metadata.total_bytes / 1024).toFixed(1)} KB source indexed</span>
          </div>

          <div>
            {metadata.analysis_status === 'completed' ? (
              <span className="inline-flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Full Analysis Complete
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 text-amber-400 font-medium">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                Partial Analysis (Resource Limit Reached)
              </span>
            )}
          </div>
        </div>

        {/* Partial Limits Warning if applicable */}
        {metadata.analysis_status === 'partial' && metadata.limits_exceeded.length > 0 && (
          <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs text-amber-300 space-y-1">
            <p className="font-semibold flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5" />
              Analysis Boundaries Applied
            </p>
            <p className="text-amber-200/80 leading-relaxed">
              {metadata.status_message ||
                'To safeguard system stability, analysis limits were applied. Core source files and manifests were successfully processed.'}
            </p>
          </div>
        )}
      </div>

      {/* Grid: Languages Breakdown & Entry Points */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Language Breakdown Card */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <FileCode2 className="w-4 h-4 text-indigo-400" />
              Programming Languages
            </h3>
            <span className="text-xs text-slate-400">
              {languages?.total_supported_files || 0} classified files
            </span>
          </div>

          {/* Visual Percentage Bar */}
          {languages && Object.keys(languages.percentages).length > 0 && (
            <div className="w-full h-3 rounded-full overflow-hidden flex bg-slate-800">
              {Object.entries(languages.percentages).map(([lang, pct]) => (
                <div
                  key={lang}
                  style={{
                    width: `${pct}%`,
                    backgroundColor: LANGUAGE_COLORS[lang] || '#6366f1',
                  }}
                  title={`${lang}: ${pct}%`}
                  className="h-full transition-all duration-300"
                />
              ))}
            </div>
          )}

          {/* Languages List */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            {languages &&
              Object.entries(languages.percentages).map(([lang, pct]) => {
                const count = languages.languages[lang] || 0
                const color = LANGUAGE_COLORS[lang] || '#6366f1'
                return (
                  <div
                    key={lang}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 border border-slate-800/80 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: color }}
                      />
                      <span className="font-medium text-slate-200">{lang}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-semibold text-white">{pct}%</span>
                      <span className="text-slate-400 text-[10px] ml-1">({count} files)</span>
                    </div>
                  </div>
                )
              })}
          </div>
        </div>

        {/* Detected Entry Points Card */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              Detected Entry Points
            </h3>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950/60 text-indigo-400 border border-indigo-800/40">
              {entryPoints.length} detected
            </span>
          </div>

          {entryPoints.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400 rounded-xl bg-slate-950/40 border border-slate-800/60">
              No conventional entry points automatically identified. Explore the file tree to trace execution.
            </div>
          ) : (
            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
              {entryPoints.map((ep) => (
                <div
                  key={ep.file_path}
                  onClick={() => onSelectFile(ep.file_path)}
                  className="p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 cursor-pointer transition-all duration-200 group space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-indigo-300 group-hover:text-indigo-200">
                        {ep.file_path}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          ep.confidence === 'confirmed'
                            ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60'
                            : 'bg-blue-950/60 text-blue-400 border-blue-800/60'
                        }`}
                      >
                        {ep.confidence.toUpperCase()}
                      </span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 leading-snug">
                    <strong className="text-slate-300">Rule:</strong> {ep.detection_method}
                  </p>

                  <div className="p-1.5 rounded bg-slate-950/80 font-mono text-[11px] text-slate-300 truncate">
                    {ep.evidence}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
