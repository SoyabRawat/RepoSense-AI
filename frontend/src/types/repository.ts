/**
 * TypeScript interfaces matching RepoSense AI Phase 2 backend schemas.
 */

export interface RepoMetadata {
  repository_id: string
  owner: string
  name: string
  full_name: string
  canonical_url: string
  default_branch: string
  commit_sha: string
  description?: string | null
  stars: number
  forks: number
  primary_language?: string | null
  license?: string | null
  file_count: number
  total_bytes: number
  analysis_timestamp: string
  analysis_status: 'completed' | 'partial' | 'failed'
  status_message?: string | null
  limits_exceeded: string[]
}

export interface FileNode {
  path: string
  name: string
  type: 'file' | 'directory'
  size: number
  language?: string | null
  is_supported: boolean
  is_entry_point: boolean
  children?: FileNode[] | null
}

export interface FileContentResponse {
  path: string
  language?: string | null
  size: number
  content: string
  line_count: number
  truncated: boolean
}

export interface LanguageBreakdown {
  languages: Record<string, number>
  percentages: Record<string, number>
  byte_counts: Record<string, number>
  total_supported_files: number
  total_repository_files: number
}

export interface EntryPointInfo {
  file_path: string
  language: string
  detection_method: string
  evidence: string
  confidence: 'confirmed' | 'likely' | 'possible'
}

export interface ImportRelationship {
  source_file: string
  target_module: string
  resolved_target_file?: string | null
  relationship_type: 'internal_import' | 'external_dependency' | 'manifest_dependency'
  source_line?: number | null
  resolution_status: 'resolved' | 'external' | 'unresolved'
}

export interface ArchitectureNode {
  id: string
  label: string
  type: 'entry_point' | 'file' | 'module' | 'external_package'
  file_path?: string | null
  language?: string | null
  metadata: Record<string, any>
}

export interface ArchitectureEdge {
  id: string
  source: string
  target: string
  type: 'imports' | 'depends_on' | 'declares_dependency'
  label?: string | null
  evidence?: string | null
}

export interface ArchitectureGraph {
  nodes: ArchitectureNode[]
  edges: ArchitectureEdge[]
  summary: Record<string, any>
}

export interface SearchResult {
  file_path: string
  line_number: number
  line_content: string
  context_before: string[]
  context_after: string[]
  language?: string | null
}

export interface SearchResponse {
  query: string
  total_matches: number
  results: SearchResult[]
  is_partial: boolean
}

export interface Citation {
  file_path: string
  start_line: number
  end_line: number
  repository_revision: string
  github_url?: string | null
  snippet?: string | null
  is_valid: boolean
}

export interface AskRequest {
  question: string
  mode: 'beginner' | 'developer'
}

export interface AskResponse {
  question: string
  answer: string
  mode: 'beginner' | 'developer'
  provider: string
  citations: Citation[]
  evidence_used: Citation[]
  disclaimer?: string | null
}
