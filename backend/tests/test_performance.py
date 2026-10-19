"""Performance and latency benchmarks for static analysis, search, and graph generation."""

import time
import pytest
from app.services.static_analysis import (
    parse_python_imports,
    parse_jsts_imports,
    analyze_repository_relationships,
)
from app.services.entry_point_detection import detect_entry_points
from app.services.search_engine import search_repository_files
from app.services.architecture_graph import build_architecture_graph
from app.schemas.repository import EntryPointInfo, ImportRelationship


def test_performance_python_and_jsts_ast_parsing() -> None:
    """Benchmark AST import analysis across a synthetic batch of 100 source files."""
    py_code = """
import os
import sys
from posixpath import join, dirname
from app.core.config import get_settings
from app.schemas.repository import RepoMetadata
from ..models import User

def handler():
    pass
"""
    ts_code = """
import React, { useState, useEffect } from 'react';
import { Sparkles, Layers } from 'lucide-react';
import { repoService } from '../services/repoService';
import type { RepoMetadata } from '@/types/repository';

export const Component = () => null;
"""
    files = {}
    for i in range(50):
        files[f"src/module_{i}.py"] = py_code
        files[f"src/components/Comp_{i}.tsx"] = ts_code

    all_files_set = set(files.keys())

    t0 = time.perf_counter()
    relationships = analyze_repository_relationships(files)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # 100 files with multiple imports each
    assert len(relationships) > 400
    # AST parsing 100 files should easily complete in under 250ms
    assert elapsed_ms < 500, f"AST parsing took {elapsed_ms:.2f}ms (threshold 500ms)"


def test_performance_search_engine_throughput() -> None:
    """Benchmark full-text search throughput across 100 files with 200 lines each (20,000 lines)."""
    line_pattern = "    logger.info('Processing transaction for user %s', user_id)\n"
    target_pattern = "    critical_symbol_found(token_id)\n"

    files = {}
    for i in range(100):
        # 200 lines per file
        content = (line_pattern * 100) + target_pattern + (line_pattern * 99)
        files[f"service/worker_{i}.py"] = content

    t0 = time.perf_counter()
    resp = search_repository_files(files=files, query="critical_symbol_found", max_results=50)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert resp.total_matches == 100
    assert len(resp.results) == 50  # Capped at max_results
    assert resp.is_partial is True
    # Search across 20,000 lines should execute in under 50ms
    assert elapsed_ms < 100, f"Search engine took {elapsed_ms:.2f}ms (threshold 100ms)"


def test_performance_architecture_graph_generation() -> None:
    """Benchmark graph layout and edge building with 150 interconnected nodes."""
    entry_points = [
        EntryPointInfo(
            file_path=f"entry_{i}.py",
            language="Python",
            detection_method="main",
            evidence="if __name__ == '__main__':",
            confidence="confirmed",
        )
        for i in range(10)
    ]

    relationships = []
    for i in range(100):
        relationships.append(
            ImportRelationship(
                source_file=f"src/file_{i}.py",
                target_module=f"src/file_{(i + 1) % 100}.py",
                resolved_target_file=f"src/file_{(i + 1) % 100}.py",
                relationship_type="internal_import",
                source_line=i + 1,
                resolution_status="resolved",
            )
        )
        relationships.append(
            ImportRelationship(
                source_file=f"src/file_{i}.py",
                target_module="fastapi",
                resolved_target_file=None,
                relationship_type="external_dependency",
                source_line=1,
                resolution_status="external",
            )
        )

    t0 = time.perf_counter()
    graph = build_architecture_graph(relationships, entry_points, {})
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert len(graph.nodes) > 100
    assert len(graph.edges) > 100
    # Graph generation and coordinate positioning should execute in under 30ms
    assert elapsed_ms < 50, f"Graph generation took {elapsed_ms:.2f}ms (threshold 50ms)"
