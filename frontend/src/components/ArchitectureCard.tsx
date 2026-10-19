import React from 'react'
import { Cpu, FileCode2, BookOpen, ExternalLink, Terminal } from 'lucide-react'

export const ArchitectureCard: React.FC = () => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
          <Cpu className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-white">System Architecture & Specs</h2>
          <p className="text-xs text-slate-400">
            Verified technology stack and technical documentation links
          </p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tech Stack Specs */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <FileCode2 className="w-4 h-4 text-blue-400" /> Verified Technology Foundation
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between p-2 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400">Frontend Engine</span>
              <span className="text-slate-200 font-mono">React 19 + TypeScript + Vite 8</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400">Backend API</span>
              <span className="text-slate-200 font-mono">FastAPI + Uvicorn (Python 3.14)</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400">Design System</span>
              <span className="text-slate-200 font-mono">Tailwind CSS + Lucide Icons</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400">Automated Testing</span>
              <span className="text-slate-200 font-mono">Pytest (Backend) + Vitest (Frontend)</span>
            </div>
          </div>
        </div>

        {/* Documentation Links */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-emerald-400" /> Architectural Specifications
          </h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-medium text-slate-200 block">ARCHITECTURE</span>
                <span className="text-[10px] text-slate-400">System topology & flow</span>
              </div>
              <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-medium text-slate-200 block">REQUIREMENTS</span>
                <span className="text-[10px] text-slate-400">Traceable FR/NFR IDs</span>
              </div>
              <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-medium text-slate-200 block">SECURITY</span>
                <span className="text-[10px] text-slate-400">Trust model & SSRF defense</span>
              </div>
              <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-medium text-slate-200 block">ROADMAP</span>
                <span className="text-[10px] text-slate-400">3-phase milestones</span>
              </div>
              <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
            </div>
          </div>

          <div className="p-2.5 rounded bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-400 flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span>npm run test:run &nbsp;|&nbsp; pytest backend/tests</span>
          </div>
        </div>
      </div>
    </div>
  )
}
