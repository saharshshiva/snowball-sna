# Methodology — Snowball SNA

## 1. Snowball Sampling

Snowball sampling is a **non-probability sampling method** used in social research when the target population is hard to reach. Initial participants (seeds) refer further participants, creating a "snowball" effect across waves (levels).

### Sampling Waves (Levels)

| Level | Meaning |
|-------|---------|
| 0 | Initial seeds — directly recruited by the researcher |
| 1 | Nominated by Level 0 seeds |
| 2 | Nominated by Level 1 participants |
| 3–5 | Subsequent referral waves |

---

## 2. Network Representation

### Directed Graph
Ties are represented as **directed (unidirectional)** edges because snowball sampling has an inherent recruitment direction:

```
Recruiter ──→ Recruit
(Level n)      (Level n+1)
```

Self-loops (`A → A`) are not analytically meaningful in recruitment networks and have been removed (3 removed: P69, P18, P35).

### Nodes: 100 respondents
### Edges: 97 directed ties (after cleaning)

---

## 3. Centrality Measures

| Measure | Formula | What it tells us |
|---------|---------|-----------------|
| **Degree** | in-deg + out-deg | Overall connectivity |
| **In-degree** | Count of incoming ties | How many people recruited this person |
| **Out-degree** | Count of outgoing ties | How many people this person recruited |
| **Betweenness** | Fraction of shortest paths through node | Bridge/broker role in network |
| **Closeness** | Inverse of avg shortest path | How quickly info can reach all others |
| **Eigenvector** | Recursive — neighbour centrality | Connected to well-connected nodes |

---

## 4. Community Detection

**Algorithm:** Greedy Modularity Maximisation (Clauset-Newman-Moore)

Modularity Q measures the fraction of edges within communities minus the expected fraction if edges were randomly distributed:

```
Q = Σ [ (e_ii / m) - (a_i / 2m)² ]
```

- Q = 0.69 indicates **strong community structure**
- 27 communities found from 100 nodes

---

## 5. Network Metrics Explained

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Density | 0.0097 | Very sparse — typical for snowball samples |
| Avg Clustering | 0.015 | Low clustering — chain-like referral structure |
| Components | 20 | Multiple disconnected sub-networks |
| Avg Path Length | 5.21 (LCC) | Moderate separation in largest component |

---

## 6. Visualisation Design Choices

- **Level color encoding**: Immediate visual separation of waves
- **Gold dashed ring**: Distinguishes seed nodes regardless of level
- **Node size ∝ degree**: Visually encodes connectivity
- **Directed arrows**: Shows recruitment flow direction
- **Force-directed layout**: Naturally clusters connected nodes

---

*TISS SEM 6 — Social Network Analysis, April 2026*
