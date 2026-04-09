# Snowball Network Analysis — Social Network Visualization

[![Deployed on Vercel](https://img.shields.io/badge/Deployed-Vercel-black?logo=vercel)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![D3.js](https://img.shields.io/badge/D3.js-v7-orange?logo=d3.js)](https://d3js.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-pink)](LICENSE)

> An interactive social network analysis (SNA) visualization of a **snowball sampling** dataset — featuring directed recruitment ties, seed hierarchy, gender/age breakdown, and centrality analysis.

---

## 🌐 Live Demo

👉 **[View on Vercel →](https://your-vercel-url.vercel.app)**  
_(URL will be updated after first deploy)_

---

## 📊 Dataset

**Source:** `snowball_example.xlsx`  
**Sheets:**

| Sheet | Rows | Columns | Description |
|-------|------|---------|-------------|
| `nodes` | 100 | ID, Seed, Gender, Age_Cat, Level | All respondents |
| `ties`  | 97  | From, To | Directed recruitment ties (self-loops removed) |

### Node Attributes

| Attribute | Values | Description |
|-----------|--------|-------------|
| `ID` | P01–P100 | Unique respondent identifier |
| `Seed` | 0 / 1 | Whether the person was an initial seed |
| `Gender` | Male / Female | Respondent gender |
| `Age_Cat` | Adult / Minor | Age category |
| `Level` | 0–5 | Snowball wave/level of recruitment |

### Data Cleaning

Three self-loop ties were removed to produce valid directed edges:
- `P69 → P69`
- `P18 → P18`  
- `P35 → P35`

---

## 🎨 Interactive Web Visualization (`index.html`)

Built with **D3.js v7** — a fully self-contained HTML file, no server required.

### Features

- **Directed force-directed graph** — arrows show recruitment direction (recruiter → recruit)
- **Color hierarchy by level** (0–5): Gold → Hot Pink → Fuchsia → Lavender → Rose → Coral
- **Seed node identification** — dashed gold ring around all `Seed = 1` nodes
- **Node size ∝ degree** — more connected nodes appear larger
- **Gender symbols** — ♂/♀ displayed inside each node
- **Filter pills** — filter by Seeds, Non-Seeds, Male, Female, Adult, Minor
- **Level legend** — click any level to isolate it in the graph
- **Node inspector** — click a node to see full attributes + in/out degree
- **Ego network highlight** — clicked node's neighbors highlighted, rest dimmed
- **↺ Reset button** — clears all filters, resets zoom, unpins all nodes, reheats simulation
- **Layout controls** — adjust link distance, repulsion, link strength
- **Zoom controls** — zoom in/out/reset
- **Scrollable** — network insights section below the graph
- **Pink color scheme** throughout

### Running Locally

Just open the file:
```bash
open index.html
# or
python3 -m http.server 8080
# then visit http://localhost:8080
```

---

## 🐍 Python Analysis (`sna_analysis.py`)

Full social network analysis using **NetworkX**, **Matplotlib**, and **Seaborn**.

### Requirements

```bash
pip install networkx matplotlib pandas numpy seaborn openpyxl
```

### Run

```bash
python3 sna_analysis.py
```

### Output — 8 Figures (saved to `figures/`)

| File | Description |
|------|-------------|
| `01_network_graph.png` | Full spring-layout network graph with level colors and seed rings |
| `02_degree_distribution.png` | In-degree, out-degree, and total degree histograms |
| `03_centrality_heatmap.png` | Normalised heatmap of top 20 nodes across 4 centrality measures |
| `04_level_composition.png` | Seed/non-seed, gender, and age distribution per level |
| `05_ego_networks_seeds.png` | Ego networks of the 4 highest-degree seed nodes |
| `06_gender_age_breakdown.png` | Donut charts + degree violin per level |
| `07_community_detection.png` | Greedy modularity community detection |
| `08_summary_dashboard.png` | All key stats in one dashboard |

### Key Results

| Metric | Value |
|--------|-------|
| Nodes | 100 |
| Directed Edges | 97 |
| Seeds (Seed=1) | 61 |
| Levels | 0–5 |
| Density | 0.0097 |
| Avg. Clustering | 0.0153 |
| Connected Components | 20 |
| Communities (Modularity) | 27 (Q=0.69) |
| Most Connected Node | P65 (degree 8) |
| Highest Betweenness | P10 (0.192) |

---

## 📁 Project Structure

```
snoball/
├── index.html              # Interactive D3.js network visualization
├── sna_analysis.py         # Python SNA script (NetworkX + Matplotlib)
├── snowball_example.xlsx   # Dataset (nodes + directed ties)
├── figures/                # Generated analysis charts
│   ├── 01_network_graph.png
│   ├── 02_degree_distribution.png
│   ├── 03_centrality_heatmap.png
│   ├── 04_level_composition.png
│   ├── 05_ego_networks_seeds.png
│   ├── 06_gender_age_breakdown.png
│   ├── 07_community_detection.png
│   └── 08_summary_dashboard.png
├── README.md               # This file
├── METHODOLOGY.md          # SNA methodology notes
├── .gitignore
└── vercel.json             # Vercel deployment config
```

---

## 🔬 Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for detailed notes on:
- Snowball sampling theory
- Directed vs undirected networks
- Centrality measures used
- Community detection algorithm

---

## 🚀 Deployment

Deployed via **Vercel** as a static site — `index.html` is the entry point.

```bash
npx vercel --prod
```

---

## 📄 License

MIT — free to use, adapt, and share with attribution.

---

*Built for TISS SEM 6 — Social Network Analysis, April 2026*
