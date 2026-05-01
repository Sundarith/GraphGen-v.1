from collections.abc import Iterable
from typing import Any, List, Optional, Tuple

from graphgen.bases import BaseGraphStorage, BasePartitioner
from graphgen.bases.datatypes import Community


class OverlappingDFSPartitioner(BasePartitioner):
    """
    Overlapping DFS partitioner that creates one community per edge-chain.

    At depth=1: yields (Node A, Edge, Node B) — One-Hop
    At depth=2: yields (Node A, Edge1, Node B, Edge2, Node C) — Two-Hop

    Unlike the standard DFSPartitioner which locks nodes into one community,
    this partitioner allows any node to appear in multiple communities,
    ensuring every relationship path gets its own dedicated Q&A prompt.

    Args:
        anchor_node: Optional substring filter. If set, only chains starting
                     from a node matching this string will be yielded.
        depth: Number of hops to walk per chain. Default is 1.
    """

    def partition(
        self,
        g: BaseGraphStorage,
        anchor_node: Optional[str] = None,
        depth: int = 1,
        **kwargs: Any,
    ) -> Iterable[Community]:
        # Build bidirectional adjacency: node_id -> list of (neighbor_id, edge_data)
        # Includes both outgoing (u→v) and incoming (v→u) edges so DFS can
        # traverse in either direction. Cycle prevention in the walk prevents
        # infinite loops.
        edges = g.get_all_edges()
        adjacency: dict[str, List[Tuple[str, dict]]] = {}
        for u, v, edge_data in edges:
            adjacency.setdefault(u, []).append((v, edge_data))   # outgoing
            adjacency.setdefault(v, []).append((u, edge_data))   # incoming (reverse)

        nodes = g.get_all_nodes()
        node_ids = [n[0] for n in nodes]

        community_idx = 0
        for start_node in node_ids:
            # Apply anchor filter on the start node only
            if anchor_node and anchor_node.lower() not in start_node.lower():
                continue

            # DFS walk to find all chains of exactly `depth` edges
            # Each stack entry: (current_node, chain_nodes, chain_edges)
            stack = [([start_node], [])]

            while stack:
                chain_nodes, chain_edges = stack.pop()

                if len(chain_edges) == depth:
                    # Emit this complete chain as a community
                    yield Community(
                        id=f"chain_{community_idx}",
                        nodes=chain_nodes,
                        edges=chain_edges,
                    )
                    community_idx += 1
                    continue

                current = chain_nodes[-1]
                for neighbor, edge_data in adjacency.get(current, []):
                    # Avoid cycles within a single chain
                    if neighbor not in chain_nodes:
                        stack.append(
                            (chain_nodes + [neighbor], chain_edges + [(current, neighbor)])
                        )


