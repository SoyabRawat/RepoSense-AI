import React from 'react'
import { Layers, CheckCircle2, Clock, ShieldAlert } from 'lucide-react'

export const PhaseTracker: React.FC = () => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white">Three-Phase Roadmap</h2>
          <p className="text-xs text-slate-400">
            Strict phase boundaries governing project development
          </p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Phase 1 */}
        <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80">
          <div className="flex items-center gap-2 text-slate-300 font-semibold text-sm mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Phase 1: Foundation & Arch
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Establish project architecture, verified local environments, and health-checked frontend/backend boundary.
          </p>
          <ul className="text-[11px] space-y-1.5 text-slate-400">
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Requirements & Architecture Docs
            </li>
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              FastAPI Health API & Logging
            </li>
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              React + Vite + Tailwind Scaffold
            </li>
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Initial Pytest & Vitest Suites
            </li>
          </ul>
        </div>

        {/* Phase 2 */}
        <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80">
          <div className="flex items-center gap-2 text-slate-300 font-semibold text-sm mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Phase 2: Core Development
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Public GitHub repo ingestion, AST parsing, dependency graphs, symbol search, and source-grounded AI explanations.
          </p>
          <ul className="text-[11px] space-y-1.5 text-slate-400">
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Sandboxed GitHub Ingestion
            </li>
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              AST Import Analysis & React Flow
            </li>
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Keyword & Symbol Code Search
            </li>
            <li className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Source-Grounded AI Explanations
            </li>
          </ul>
        </div>

        {/* Phase 3 */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-indigo-500/40 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-2.5 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] font-semibold tracking-wider rounded-bl uppercase">
            Current Phase
          </div>
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm mb-2">
            <Clock className="w-4 h-4 text-amber-400" />
            Phase 3: Testing & Release
          </div>
          <p className="text-xs text-slate-300 mb-3">
            Comprehensive testing, SSRF security audits, performance profiling, and production Docker containerization.
          </p>
          <ul className="text-[11px] space-y-1.5 text-slate-300">
            <li className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              End-to-End Test Automation
            </li>
            <li className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Security Penetration Audits
            </li>
            <li className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Multi-Stage Docker Packaging
            </li>
            <li className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Public Open-Source Release (v0.3.0)
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-4 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
        <span>
          <strong>Phase Boundary Rule:</strong> Phase 3 is the final planned phase. All development focuses on testing, security hardening, performance profiling, documentation, and open-source release preparation.
        </span>
      </div>
    </div>
  )
}
