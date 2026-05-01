# Graph Partitioning Theory: Leiden Algorithm Mechanics

This document explains the core mathematical and logical behavior of the `LeidenPartitioner` used in the GraphGen engine, specifically concerning how it groups nodes into communities and how parameters like `max_size` and `random_seed` affect the final LLM prompts.

## 1. Crawler vs. Optimizer
*   **Crawlers (BFS / DFS):** These algorithms pick a starting "Seed" node and blindly walk outward along the edges until they hit a limit. They do not care about the density or semantic meaning of the cluster.
*   **Optimizers (Leiden):** Leiden looks at the entire graph holistically. It attempts to maximize a mathematical score called **Modularity** (Density). It groups nodes that are highly connected to each other while ensuring they have very few connections to outside nodes.

## 2. The "Bridge" Effect (Indirect Connections)
The Modularity math **only calculates direct edges** between nodes. 
However, two nodes that never directly touch (e.g., `BlueSmacking` and `Bluetooth`) will frequently end up in the exact same community. This happens because of the **Snowball Effect**. 
If both nodes connect to a shared third node (e.g., `L2CAP Protocol`), that third node acts as a mathematical "bridge," raising the density score for the entire group and pulling them all into the same community.

## 3. The `max_size` Constraint & "Severed Edges"
The `max_size` parameter (e.g., 15) acts as a strict ceiling, not a quota. If Leiden finds a perfectly dense semantic group of 5 nodes, it will stop there rather than pulling in unrelated nodes to hit the number 15.

**The Danger of Severed Edges:**
When a community is finalized, the engine uses an "Induced Subgraph" rule. If a node inside the community has an edge pointing to a node *outside* the community, **that edge is deleted from the final LLM prompt**. 
*   *Tradeoff:* This prevents the LLM from hallucinating missing definitions, but if the `max_size` is too small, a "Problem" node might be separated from its "Solution" node, meaning the LLM will never see them together to form a reasoning chain.

## 4. The Role of the `random_seed`
If Modularity is strict math, why does a random seed change the communities?
For the tightly connected "Core" of a community, the random seed changes nothing. Deeply connected nodes will always merge.

Randomness affects the **Borders** in two ways:
1.  **The Mathematical Tie (Fence Sitters):** If Node X sits between Group 1 and Group 2, and joining either group provides the exact same density boost (+0.2), the algorithm uses the random seed as a coin flip to break the tie.
2.  **The Race for the Last Seat:** If a community has 13 nodes, and `max_size` is 15, there are only 2 seats left. If 10 "fringe" nodes are connected to the community and want to join, the random seed determines the checklist order. The first 2 fringe nodes evaluated get the seats; the remaining 8 are locked out.

By changing the `random_seed`, developers can "shake the box," causing the algorithm to shift the borders slightly. This allows the engine to generate completely new, fresh Multi-Hop Q&A pairs from the exact same underlying graph without causing the LLM to overfit on identical data.
