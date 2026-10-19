import React, { useState } from 'react'
import {
  Sparkles,
  GitBranch,
  ShieldCheck,
  ChevronRight,
  Server,
  Layers,
} from 'lucide-react'
import { useHealth } from '../hooks/useHealth'
import { ConnectivityCard } from '../components/ConnectivityCard'
import { PhaseTracker } from '../components/PhaseTracker'
import { ArchitectureCard } from '../components/ArchitectureCard'
import { RepoSearchBar } from '../components/RepoSearchBar'
import { MainWorkspace } from '../components/MainWorkspace'
import { repoService } from '../services/repoService'
import type {
  ArchitectureGraph,
  EntryPointInfo,
  FileNode,
  LanguageBreakdown,
  RepoMetadata,
} from '../types/repository'

export const LandingPage: React.FC = () => {
  const { data, isLoading: isHealthLoading, error: healthError, latencyMs, lastChecked, refetch } = useHealth()

  // Repository analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [activeStep, setActiveStep] = useState(0)

  // Current analyzed repository data
  const [metadata, setMetadata] = useState<RepoMetadata | null>(null)
  const [tree, setTree] = useState<FileNode | null>(null)
  const [languages, setLanguages] = useState<LanguageBreakdown | null>(null)
  const [entryPoints, setEntryPoints] = useState<EntryPointInfo[]>([])
  const [graph, setGraph] = useState<ArchitectureGraph | null>(null)

  // View mode: 'analysis' or 'status'
  const [showSystemDashboard, setShowSystemDashboard] = useState(false)

  const handleAnalyze = async (url: string) => {
    setIsAnalyzing(true)
    setAnalysisError(null)
    setActiveStep(0)

    try {
      // Step 1: Validating URL & SSRF
      setActiveStep(0)
      await new Promise((r) => setTimeout(r, 200))

      // Step 2: Retrieving Metadata
      setActiveStep(1)
      const meta = await repoService.analyzeRepository(url)
      setMetadata(meta)

      // Step 3: Fetching Tree
      setActiveStep(2)
      const repoTree = await repoService.getTree(meta.repository_id)
      setTree(repoTree)

      // Step 4: Languages & Entry Points
      setActiveStep(3)
      const [langs, eps] = await Promise.all([
        repoService.getLanguages(meta.repository_id),
        repoService.getEntryPoints(meta.repository_id),
      ])
      setLanguages(langs)
      setEntryPoints(eps)

      // Step 5: Architecture Graph
      setActiveStep(4)
      const archGraph = await repoService.getGraph(meta.repository_id)
      setGraph(archGraph)

      // Step 6: Complete
      setActiveStep(5)
      await new Promise((r) => setTimeout(r, 200))
      setShowSystemDashboard(false)
    } catch (err: unknown) {
      setAnalysisError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <GitBranch className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-2">
                RepoSense AI
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  v0.3.0
                </span>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {metadata && (
              <button
                type="button"
                onClick={() => setShowSystemDashboard(!showSystemDashboard)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              >
                {showSystemDashboard ? (
                  <>
                    <Layers className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Back to Repository</span>
                  </>
                ) : (
                  <>
                    <Server className="w-3.5 h-3.5 text-slate-400" />
                    <span>System Status</span>
                  </>
                )}
              </button>
            )}

            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Phase 3: Release
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Search Bar is always prominent */}
        <section aria-labelledby="repo-search-heading">
          <RepoSearchBar
            onAnalyze={handleAnalyze}
            isLoading={isAnalyzing}
            error={analysisError}
            activeStep={activeStep}
          />
        </section>

        {/* View Mode 1: Active Repository Workspace */}
        {metadata && !showSystemDashboard ? (
          <section aria-labelledby="workspace-heading">
            <MainWorkspace
              metadata={metadata}
              tree={tree}
              languages={languages}
              entryPoints={entryPoints}
              graph={graph}
            />
          </section>
        ) : (
          /* View Mode 2: Welcome / System Status Dashboard */
          <div className="space-y-8">
            {/* Hero / Vision introduction */}
            <div className="text-center max-w-3xl mx-auto space-y-4 pt-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-slate-900 border border-slate-800 text-slate-300">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Phase 3 Testing, Security &amp; Release Ready
              </div>

              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
                Understand Unfamiliar Codebases{' '}
                <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
                  In Minutes
                </span>
              </h1>

              <p className="text-slate-400 text-sm sm:text-base leading-relaxed max-w-2xl mx-auto">
                RepoSense AI combines deterministic static analysis, abstract syntax tree (AST) parsing,
                interactive dependency graph visualization, and source-grounded code explanations with verifiable file references.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-4 pt-2 text-xs text-slate-400">
                <div className="flex items-center gap-1.5">
                  <ChevronRight className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Public GitHub Ingestion</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ChevronRight className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Interactive Dependency Graph</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ChevronRight className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Full-Text Code Search</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ChevronRight className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Source-Grounded Citations</span>
                </div>
              </div>
            </div>

            {/* Live Backend Connectivity Card */}
            <section aria-labelledby="connectivity-heading">
              <ConnectivityCard
                data={data}
                isLoading={isHealthLoading}
                error={healthError}
                latencyMs={latencyMs}
                lastChecked={lastChecked}
                onRetry={refetch}
              />
            </section>

            {/* Phase Progression Tracker */}
            <section aria-labelledby="roadmap-heading">
              <PhaseTracker />
            </section>

            {/* Architecture Card */}
            <section aria-labelledby="architecture-heading">
              <ArchitectureCard />
            </section>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-8 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4 space-y-2">
          <p>RepoSense AI — Open-Source Repository Understanding Tool</p>
          <p>Phase 3 Release &bull; FastAPI, React 19, TypeScript, Vite, Tailwind CSS &bull; MIT License</p>
        </div>
      </footer>
    </div>
  )
}
