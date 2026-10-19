/**
 * API client service for RepoSense AI repository analysis, exploration, and search.
 */

import { fetchApi } from './api'
import type {
  ArchitectureGraph,
  AskRequest,
  AskResponse,
  EntryPointInfo,
  FileContentResponse,
  FileNode,
  LanguageBreakdown,
  RepoMetadata,
  SearchResponse,
} from '../types/repository'

export const repoService = {
  /**
   * Submit repository URL for ingestion and static analysis.
   */
  async analyzeRepository(url: string): Promise<RepoMetadata> {
    return fetchApi<RepoMetadata>('/api/v1/repositories/analyze', {
      method: 'POST',
      body: JSON.stringify({ url }),
    })
  },

  /**
   * Retrieve metadata for an analyzed repository.
   */
  async getMetadata(repoId: string): Promise<RepoMetadata> {
    return fetchApi<RepoMetadata>(`/api/v1/repositories/${encodeURIComponent(repoId)}`)
  },

  /**
   * Retrieve full directory and file tree.
   */
  async getTree(repoId: string): Promise<FileNode> {
    return fetchApi<FileNode>(`/api/v1/repositories/${encodeURIComponent(repoId)}/tree`)
  },

  /**
   * Retrieve file content with line numbers.
   */
  async getFileContent(repoId: string, path: string): Promise<FileContentResponse> {
    return fetchApi<FileContentResponse>(
      `/api/v1/repositories/${encodeURIComponent(repoId)}/files/content?path=${encodeURIComponent(path)}`
    )
  },

  /**
   * Retrieve programming language breakdown.
   */
  async getLanguages(repoId: string): Promise<LanguageBreakdown> {
    return fetchApi<LanguageBreakdown>(`/api/v1/repositories/${encodeURIComponent(repoId)}/languages`)
  },

  /**
   * Retrieve detected application entry points.
   */
  async getEntryPoints(repoId: string): Promise<EntryPointInfo[]> {
    return fetchApi<EntryPointInfo[]>(`/api/v1/repositories/${encodeURIComponent(repoId)}/entry-points`)
  },

  /**
   * Retrieve architecture graph nodes and edges.
   */
  async getGraph(repoId: string): Promise<ArchitectureGraph> {
    return fetchApi<ArchitectureGraph>(`/api/v1/repositories/${encodeURIComponent(repoId)}/graph`)
  },

  /**
   * Full-text source code search.
   */
  async search(
    repoId: string,
    query: string,
    caseSensitive: boolean = false,
    pathFilter?: string,
    langFilter?: string
  ): Promise<SearchResponse> {
    const params = new URLSearchParams({
      q: query,
      case_sensitive: String(caseSensitive),
    })
    if (pathFilter) params.append('path_filter', pathFilter)
    if (langFilter) params.append('language_filter', langFilter)

    return fetchApi<SearchResponse>(
      `/api/v1/repositories/${encodeURIComponent(repoId)}/search?${params.toString()}`
    )
  },

  /**
   * Ask AI a source-grounded question.
   */
  async ask(repoId: string, question: string, mode: 'beginner' | 'developer'): Promise<AskResponse> {
    const payload: AskRequest = { question, mode }
    return fetchApi<AskResponse>(`/api/v1/repositories/${encodeURIComponent(repoId)}/ask`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
}
