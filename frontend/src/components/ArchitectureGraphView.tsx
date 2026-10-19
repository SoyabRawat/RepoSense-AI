import React, { useMemo, useState } from 'react'
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  Panel,
  MarkerType,
  type Node,
  type Edge,
} from '@xyflow/react'
import {
  FileCode,
  Sparkles,
  Package,
  Layers,
  ArrowRight,
  Filter,
} from 'lucide-react'
import type { ArchitectureGraph } from '../types/repository'

interface ArchitectureGraphViewProps {
  graph: ArchitectureGraph | null
  onSelectFile: (path: string) => void
}

export const ArchitectureGraphView: React.FC<ArchitectureGraphViewProps> = ({
  graph,
  onSelectFile,
}) => {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Map backend ArchitectureGraph to ReactFlow nodes & edges
  const flowNodes: Node[] = useMemo(() => {
    if (!graph) return []

    return graph.nodes
      .filter((n) => {
        if (filterType !== 'all' && n.type !== filterType) return false
        if (searchQuery && !n.label.toLowerCase().includes(searchQuery.toLowerCase())) return false
        return true
      })
      .map((node) => {
        const isEntry = node.type === 'entry_point'
        const isPkg = node.type === 'external_package'

        const pos = node.metadata?.position || { x: 100, y: 100 }

        return {
          id: node.id,
          position: pos,
          data: {
            label: (
              <div className="flex flex-col gap-1 p-1">
                <div className="flex items-center gap-1.5 font-semibold text-xs truncate">
                  {isEntry ? (
                    <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  ) : isPkg ? (
                    <Package className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  ) : (
                    <FileCode className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  )}
                  <span className="truncate">{node.label}</span>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-400">
                  <span className="px-1.5 py-0.2 rounded bg-slate-900 border border-slate-700/80">
                    {node.language || node.type}
                  </span>
                </div>
              </div>
            ),
            rawNode: node,
          },
          style: {
            background: isEntry ? '#1e1b4b' : isPkg ? '#2e1065' : '#0f172a',
            color: '#f8fafc',
            border:
              selectedNodeId === node.id
                ? '2px solid #818cf8'
                : isEntry
                ? '1px solid #6366f1'
                : isPkg
                ? '1px solid #a855f7'
                : '1px solid #334155',
            borderRadius: '12px',
            padding: '8px 12px',
            minWidth: '150px',
            maxWidth: '220px',
            boxShadow:
              selectedNodeId === node.id
                ? '0 0 15px rgba(129, 140, 248, 0.4)'
                : '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
          },
        }
      })
  }, [graph, filterType, searchQuery, selectedNodeId])

  const visibleNodeIds = useMemo(() => new Set(flowNodes.map((n) => n.id)), [flowNodes])

  const flowEdges: Edge[] = useMemo(() => {
    if (!graph) return []

    return graph.edges
      .filter((e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target))
      .map((edge) => {
        const isManifest = edge.type === 'declares_dependency'
        const isInternal = edge.type === 'imports'

        return {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label || undefined,
          animated: isInternal,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: isInternal ? '#6366f1' : isManifest ? '#a855f7' : '#64748b',
          },
          style: {
            stroke: isInternal ? '#6366f1' : isManifest ? '#a855f7' : '#64748b',
            strokeWidth: isInternal ? 2 : 1.5,
          },
          labelStyle: {
            fill: '#94a3b8',
            fontSize: 10,
            fontFamily: 'monospace',
          },
        }
      })
  }, [graph, visibleNodeIds])

  const selectedNode = useMemo(() => {
    if (!selectedNodeId || !graph) return null
    return graph.nodes.find((n) => n.id === selectedNodeId) || null
  }, [selectedNodeId, graph])

  if (!graph || graph.nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[550px] p-8 text-center bg-slate-950/80 border border-slate-800 rounded-2xl shadow-lg">
        <Layers className="w-12 h-12 text-slate-700 mb-3" />
        <h4 className="text-base font-semibold text-slate-300">No Relationships Found</h4>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          No internal file imports or package dependencies were detected for visual graph mapping.
        </p>
      </div>
    )
  }

  return (
    <div className="relative h-[650px] w-full rounded-2xl border border-slate-800 overflow-hidden bg-slate-950 shadow-2xl">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        onNodeClick={(_, node) => setSelectedNodeId(node.id)}
        onPaneClick={() => setSelectedNodeId(null)}
        fitView
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#334155" />
        <Controls className="bg-slate-900 border border-slate-800 fill-slate-300 text-slate-300" />

        {/* Top Control Panel */}
        <Panel position="top-left" className="m-3">
          <div className="flex flex-wrap items-center gap-2 p-2 rounded-xl bg-slate-900/95 border border-slate-800 shadow-xl backdrop-blur-md text-xs">
            {/* Filter buttons */}
            <div className="flex items-center gap-1">
              <Filter className="w-3.5 h-3.5 text-slate-400 ml-1" />
              {[
                { id: 'all', label: 'All Nodes' },
                { id: 'entry_point', label: 'Entry Points' },
                { id: 'file', label: 'Files' },
                { id: 'external_package', label: 'Packages' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setFilterType(f.id)}
                  className={`px-2.5 py-1 rounded-lg transition-colors font-medium ${
                    filterType === f.id
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Node Search input */}
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Find node..."
              className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-indigo-500/60"
            />

            <span className="text-[11px] text-slate-400 px-2">
              {flowNodes.length} nodes &bull; {flowEdges.length} edges
            </span>
          </div>
        </Panel>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <Panel position="bottom-right" className="m-4">
            <div className="w-80 p-4 rounded-xl bg-slate-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-xl text-xs space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="font-semibold text-slate-200 flex items-center gap-1.5 truncate">
                  {selectedNode.type === 'entry_point' ? (
                    <Sparkles className="w-4 h-4 text-amber-400" />
                  ) : selectedNode.type === 'external_package' ? (
                    <Package className="w-4 h-4 text-purple-400" />
                  ) : (
                    <FileCode className="w-4 h-4 text-indigo-400" />
                  )}
                  {selectedNode.label}
                </span>
                <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[10px] text-slate-400">
                  {selectedNode.type}
                </span>
              </div>

              {selectedNode.file_path && (
                <div className="space-y-1">
                  <span className="text-slate-400">File Path:</span>
                  <div className="p-1.5 rounded bg-slate-950 font-mono text-slate-300 break-all">
                    {selectedNode.file_path}
                  </div>
                </div>
              )}

              {selectedNode.metadata?.evidence && (
                <div className="space-y-1">
                  <span className="text-slate-400">Evidence:</span>
                  <p className="p-1.5 rounded bg-slate-950 text-slate-300 font-mono text-[11px]">
                    {selectedNode.metadata.evidence}
                  </p>
                </div>
              )}

              {selectedNode.file_path && (
                <button
                  onClick={() => onSelectFile(selectedNode.file_path!)}
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-md shadow-indigo-600/30 transition-all"
                >
                  <span>Open in Source Viewer</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </Panel>
        )}
      </ReactFlow>
    </div>
  )
}
