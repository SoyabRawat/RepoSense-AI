import React, { useState, useMemo } from 'react'
import {
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  ChevronRight,
  ChevronDown,
  Star,
  Search,
} from 'lucide-react'
import type { FileNode } from '../types/repository'

interface FileExplorerProps {
  tree: FileNode | null
  selectedPath: string | null
  onSelectFile: (path: string) => void
}

interface TreeNodeProps {
  node: FileNode
  depth: number
  selectedPath: string | null
  onSelectFile: (path: string) => void
  filterQuery: string
}

const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  depth,
  selectedPath,
  onSelectFile,
  filterQuery,
}) => {
  const [isOpen, setIsOpen] = useState(depth < 2)

  const isDirectory = node.type === 'directory'
  const isSelected = selectedPath === node.path

  // Check if this node or any child matches search query
  const matchesFilter = useMemo(() => {
    if (!filterQuery) return true
    const q = filterQuery.toLowerCase()

    const checkMatch = (n: FileNode): boolean => {
      if (n.name.toLowerCase().includes(q) || n.path.toLowerCase().includes(q)) return true
      if (n.children) {
        return n.children.some(checkMatch)
      }
      return false
    }

    return checkMatch(node)
  }, [node, filterQuery])

  if (!matchesFilter) return null

  if (isDirectory) {
    return (
      <div>
        <div
          onClick={() => setIsOpen(!isOpen)}
          style={{ paddingLeft: `${depth * 14 + 8}px` }}
          className="flex items-center gap-1.5 py-1 px-2 rounded-lg hover:bg-slate-800/60 cursor-pointer text-xs text-slate-300 hover:text-white transition-colors select-none"
        >
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          )}

          {isOpen ? (
            <FolderOpen className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          ) : (
            <Folder className="w-3.5 h-3.5 text-amber-400/80 shrink-0" />
          )}

          <span className="font-medium truncate">{node.name || 'root'}</span>
        </div>

        {isOpen && node.children && (
          <div>
            {node.children.map((child) => (
              <TreeNode
                key={child.path}
                node={child}
                depth={depth + 1}
                selectedPath={selectedPath}
                onSelectFile={onSelectFile}
                filterQuery={filterQuery}
              />
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      onClick={() => onSelectFile(node.path)}
      style={{ paddingLeft: `${depth * 14 + 18}px` }}
      className={`flex items-center justify-between py-1 px-2 rounded-lg cursor-pointer text-xs transition-colors select-none group ${
        isSelected
          ? 'bg-indigo-600/30 text-indigo-200 border border-indigo-500/40 font-semibold'
          : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
      }`}
    >
      <div className="flex items-center gap-2 truncate">
        {node.is_supported ? (
          <FileCode
            className={`w-3.5 h-3.5 shrink-0 ${
              isSelected ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'
            }`}
          />
        ) : (
          <FileText className="w-3.5 h-3.5 shrink-0 text-slate-600" />
        )}
        <span className="truncate">{node.name}</span>
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        {node.is_entry_point && (
          <span title="Entry Point">
            <Star className="w-3 h-3 fill-amber-400 text-amber-400 shrink-0" />
          </span>
        )}
        {node.language && (
          <span className="text-[10px] text-slate-400 px-1 py-0.2 rounded bg-slate-900 border border-slate-800">
            {node.language}
          </span>
        )}
      </div>
    </div>
  )
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  tree,
  selectedPath,
  onSelectFile,
}) => {
  const [filterQuery, setFilterQuery] = useState('')

  return (
    <div className="flex flex-col h-full bg-slate-950/80 border border-slate-800 rounded-2xl overflow-hidden shadow-lg">
      {/* Header and Filter */}
      <div className="p-3 border-b border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Files & Directories
          </span>
        </div>

        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="Filter files..."
            className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60"
          />
        </div>
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5 font-mono">
        {!tree ? (
          <div className="p-6 text-center text-xs text-slate-500">No tree loaded</div>
        ) : tree.children && tree.children.length > 0 ? (
          tree.children.map((child) => (
            <TreeNode
              key={child.path}
              node={child}
              depth={0}
              selectedPath={selectedPath}
              onSelectFile={onSelectFile}
              filterQuery={filterQuery}
            />
          ))
        ) : (
          <div className="p-6 text-center text-xs text-slate-500">No files in directory</div>
        )}
      </div>
    </div>
  )
}
