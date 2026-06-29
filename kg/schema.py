from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class NodeType(str, Enum):
    SCHEME = "Scheme"
    CRITERION = "Criterion"
    BENEFIT = "Benefit"
    DOCUMENT = "Document"


class EdgeType(str, Enum):
    HAS_CRITERION = "HAS_CRITERION"
    PROVIDES = "PROVIDES"
    CITES = "CITES"


@dataclass
class Node:
    id: str
    type: NodeType
    properties: Dict[str, Any]


@dataclass
class Edge:
    source: str
    target: str
    type: EdgeType
    properties: Dict[str, Any]


__all__ = ["NodeType", "EdgeType", "Node", "Edge"]

