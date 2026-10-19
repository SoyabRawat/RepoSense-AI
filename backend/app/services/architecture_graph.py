"""Architecture graph builder transforming verified code relationships into node-link graph data."""

import posixpath
from typing import Dict, List, Set
from app.schemas.repository import ArchitectureEdge, ArchitectureGraph, ArchitectureNode, EntryPointInfo, ImportRelationship


def build_architecture_graph(
    relationships: List[ImportRelationship],
    entry_points: List[EntryPointInfo],
    files: Dict[str, str],
) -> ArchitectureGraph:
    """
    Construct nodes and edges for the React Flow architecture graph from verified static facts.
    """
    nodes: List[ArchitectureNode] = []
    edges: List[ArchitectureEdge] = []

    node_ids: Set[str] = set()
    entry_point_files = {ep.file_path for ep in entry_points}

    # 1. Create nodes for entry points
    for ep in entry_points:
        node_id = f"entry:{ep.file_path}"
        if node_id not in node_ids:
            nodes.append(
                ArchitectureNode(
                    id=node_id,
                    label=f"Entry: {posixpath.basename(ep.file_path)}",
                    type="entry_point",
                    file_path=ep.file_path,
                    language=ep.language,
                    metadata={
                        "confidence": ep.confidence,
                        "detection_method": ep.detection_method,
                        "evidence": ep.evidence,
                    },
                )
            )
            node_ids.add(node_id)

    # Helper to get or create a file node
    def get_or_create_file_node(path: str) -> str:
        if path in entry_point_files:
            return f"entry:{path}"
        node_id = f"file:{path}"
        if node_id not in node_ids:
            # Detect language from extension
            ext = posixpath.splitext(path)[1].lower()
            lang = "Source"
            if ext in (".py", ".pyw"):
                lang = "Python"
            elif ext in (".ts", ".tsx"):
                lang = "TypeScript"
            elif ext in (".js", ".jsx"):
                lang = "JavaScript"
            elif ext == ".java":
                lang = "Java"
            elif ext in (".c", ".cpp", ".h", ".hpp"):
                lang = "C/C++"

            nodes.append(
                ArchitectureNode(
                    id=node_id,
                    label=posixpath.basename(path),
                    type="file",
                    file_path=path,
                    language=lang,
                    metadata={"path": path, "dir": posixpath.dirname(path) or "."},
                )
            )
            node_ids.add(node_id)
        return node_id

    # Helper to get or create an external package node
    def get_or_create_pkg_node(pkg_name: str) -> str:
        clean_name = pkg_name.split()[0]  # strip version annotations
        node_id = f"pkg:{clean_name}"
        if node_id not in node_ids:
            nodes.append(
                ArchitectureNode(
                    id=node_id,
                    label=clean_name,
                    type="external_package",
                    file_path=None,
                    language="External",
                    metadata={"package": clean_name},
                )
            )
            node_ids.add(node_id)
        return node_id

    # 2. Process relationships to build edges and nodes
    edge_keys: Set[str] = set()

    for idx, rel in enumerate(relationships):
        src_node_id = get_or_create_file_node(rel.source_file)

        if rel.relationship_type == "internal_import" and rel.resolved_target_file:
            tgt_node_id = get_or_create_file_node(rel.resolved_target_file)
            edge_key = f"{src_node_id}->{tgt_node_id}:imports"
            if edge_key not in edge_keys and src_node_id != tgt_node_id:
                edges.append(
                    ArchitectureEdge(
                        id=f"e_{len(edges)}",
                        source=src_node_id,
                        target=tgt_node_id,
                        type="imports",
                        label="imports",
                        evidence=f"Line {rel.source_line}" if rel.source_line else None,
                    )
                )
                edge_keys.add(edge_key)

        elif rel.relationship_type == "external_dependency":
            tgt_node_id = get_or_create_pkg_node(rel.target_module)
            edge_key = f"{src_node_id}->{tgt_node_id}:depends_on"
            if edge_key not in edge_keys:
                edges.append(
                    ArchitectureEdge(
                        id=f"e_{len(edges)}",
                        source=src_node_id,
                        target=tgt_node_id,
                        type="depends_on",
                        label="depends on",
                        evidence=f"Line {rel.source_line}" if rel.source_line else None,
                    )
                )
                edge_keys.add(edge_key)

        elif rel.relationship_type == "manifest_dependency":
            tgt_node_id = get_or_create_pkg_node(rel.target_module)
            edge_key = f"{src_node_id}->{tgt_node_id}:declares"
            if edge_key not in edge_keys:
                edges.append(
                    ArchitectureEdge(
                        id=f"e_{len(edges)}",
                        source=src_node_id,
                        target=tgt_node_id,
                        type="declares_dependency",
                        label="declares",
                        evidence="Package manifest declaration",
                    )
                )
                edge_keys.add(edge_key)

    # Calculate layout coordinates (x, y) so graph renders neatly organized
    # We partition nodes into tiers:
    # Tier 0 (Entry Points): x = 50
    # Tier 1 (Internal Files): x = 400
    # Tier 2 (External Packages): x = 800
    entry_y = 60
    file_count = sum(1 for n in nodes if n.type == "file")
    pkg_count = sum(1 for n in nodes if n.type == "external_package")

    file_cols = 3 if file_count > 24 else (2 if file_count > 8 else 1)
    pkg_cols = 2 if pkg_count > 10 else 1

    file_idx = 0
    pkg_idx = 0
    spacing_y = 100
    spacing_x = 240

    for node in nodes:
        if node.type == "entry_point":
            node.metadata["position"] = {"x": 50, "y": entry_y}
            entry_y += 110
        elif node.type == "file":
            col = file_idx % file_cols
            row = file_idx // file_cols
            base_x = 360
            node.metadata["position"] = {"x": base_x + (col * spacing_x), "y": 60 + (row * spacing_y)}
            file_idx += 1
        else:
            col = pkg_idx % pkg_cols
            row = pkg_idx // pkg_cols
            base_x = 360 + (file_cols * spacing_x) + 60
            node.metadata["position"] = {"x": base_x + (col * spacing_x), "y": 60 + (row * spacing_y)}
            pkg_idx += 1

    summary = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "entry_points": len(entry_points),
        "files_connected": sum(1 for n in nodes if n.type == "file"),
        "external_packages": sum(1 for n in nodes if n.type == "external_package"),
    }

    return ArchitectureGraph(nodes=nodes, edges=edges, summary=summary)
