import React, { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  FolderTree,
  Network,
  Search,
  Sparkles,
} from 'lucide-react'
import { repoService } from '../services/repoService'
import type {
  ArchitectureGraph,
  EntryPointInfo,
  FileNode,
  LanguageBreakdown,
  RepoMetadata,
} from '../types/repository'
import { OverviewDashboard } from './OverviewDashboard'
import { FileExplorer } from './FileExplorer'
import { SourceViewer } from './SourceViewer'
import { ArchitectureGraphView } from './ArchitectureGraphView'
import { CodeSearchView } from './CodeSearchView'
import { AskAIView } from './AskAIView'

interface MainWorkspaceProps {
  metadata: RepoMetadata
  tree: FileNode | null
  languages: LanguageBreakdown | null
  entryPoints: EntryPointInfo[]
  graph: ArchitectureGraph | null
}

type TabType = 'overview' | 'explorer' | 'graph' | 'search' | 'ask'

export const MainWorkspace: React.FC<MainWorkspaceProps> = ({
  metadata,
  tree,
  languages,
  entryPoints,
  graph,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  const defaultFile =
    entryPoints.length > 0
      ? entryPoints[0].file_path
      : (tree?.children?.find((c) => c.type === 'file')?.path ?? null)

  // Selected file and line in SourceViewer
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(defaultFile)
  const [highlightLine, setHighlightLine] = useState<number | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const [fileLanguage, setFileLanguage] = useState<string | null>(null)
  const [isFileLoading, setIsFileLoading] = useState<boolean>(() => Boolean(defaultFile))
  const [fileError, setFileError] = useState<string | null>(null)

  const activeFilePath = selectedFilePath || defaultFile

  useEffect(() => {
    if (!activeFilePath) return

    let isSubscribed = true
    repoService
      .getFileContent(metadata.repository_id, activeFilePath)
      .then((resp) => {
        if (isSubscribed) {
          setFileContent(resp.content)
          setFileLanguage(resp.language || null)
          setIsFileLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (isSubscribed) {
          setFileError(err instanceof Error ? err.message : String(err))
          setFileContent(null)
          setIsFileLoading(false)
        }
      })

    return () => {
      isSubscribed = false
    }
  }, [activeFilePath, metadata.repository_id])

  const handleSelectFile = (path: string, line?: number) => {
    setSelectedFilePath(path)
    setHighlightLine(line || null)
    setIsFileLoading(true)
    setFileError(null)
  }

  const handleJumpToFile = (path: string, line: number) => {
    handleSelectFile(path, line)
    setActiveTab('explorer')
  }

  const TABS = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'explorer', label: 'Code Explorer', icon: FolderTree },
    { id: 'graph', label: 'Architecture Graph', icon: Network },
    { id: 'search', label: 'Code Search', icon: Search },
    { id: 'ask', label: 'Ask AI', icon: Sparkles },
  ]

  return (
    <div className="space-y-6">
      {/* Navigation Tabs Bar */}
      <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg backdrop-blur-md overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 shrink-0 ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
              {tab.id === 'ask' && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-white/20 text-white font-mono">
                  AI
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <OverviewDashboard
          metadata={metadata}
          languages={languages}
          entryPoints={entryPoints}
          onSelectFile={(path) => {
            handleSelectFile(path)
            setActiveTab('explorer')
          }}
        />
      )}

      {activeTab === 'explorer' && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 h-[720px]">
          <div className="md:col-span-4 h-full">
            <FileExplorer
              tree={tree}
              selectedPath={activeFilePath}
              onSelectFile={(path) => handleSelectFile(path)}
            />
          </div>
          <div className="md:col-span-8 h-full">
            <SourceViewer
              path={activeFilePath}
              content={fileContent}
              language={fileLanguage}
              isLoading={isFileLoading}
              error={fileError}
              highlightLine={highlightLine}
              commitSha={metadata.commit_sha}
              canonicalUrl={metadata.canonical_url}
            />
          </div>
        </div>
      )}

      {activeTab === 'graph' && (
        <ArchitectureGraphView
          graph={graph}
          onSelectFile={(path) => {
            handleSelectFile(path)
            setActiveTab('explorer')
          }}
        />
      )}

      {activeTab === 'search' && (
        <CodeSearchView
          repoId={metadata.repository_id}
          onJumpToFile={handleJumpToFile}
        />
      )}

      {activeTab === 'ask' && (
        <AskAIView
          repoId={metadata.repository_id}
          onJumpToFile={handleJumpToFile}
        />
      )}
    </div>
  )
}
