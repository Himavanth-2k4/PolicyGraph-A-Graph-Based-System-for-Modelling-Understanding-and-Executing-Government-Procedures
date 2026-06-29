from __future__ import annotations

from typing import Dict, List, Iterable

import networkx as nx

from .schema import Node, Edge, NodeType, EdgeType


class InMemoryGraphStore:
    """
    Simple in-memory KG using NetworkX.
    Good enough for experiments and easy to port to Neo4j later.
    """

    def __init__(self) -> None:
        self.g = nx.MultiDiGraph()

    def add_node(self, node: Node) -> None:
        self.g.add_node(node.id, type=node.type.value, **node.properties)

    def add_edge(self, edge: Edge) -> None:
        self.g.add_edge(edge.source, edge.target, key=edge.type.value, type=edge.type.value, **edge.properties)

    def get_scheme_criteria(self, scheme_id: str) -> List[Dict]:
        """
        Return criteria nodes connected to a scheme via HAS_CRITERION.
        """
        out: List[Dict] = []
        for _, tgt, key, data in self.g.out_edges(scheme_id, keys=True, data=True):
            if data.get("type") == EdgeType.HAS_CRITERION.value:
                node_data = self.g.nodes[tgt]
                out.append(
                    {
                        "criterion_id": tgt,
                        "properties": dict(node_data),
                        "edge_properties": dict(data),
                    }
                )
        return out

    def schemes(self) -> Iterable[str]:
        for nid, data in self.g.nodes(data=True):
            if data.get("type") == NodeType.SCHEME.value:
                yield nid


__all__ = ["InMemoryGraphStore"]

