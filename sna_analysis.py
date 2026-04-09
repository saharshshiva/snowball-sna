"""
=============================================================
  Snowball Sampling — Social Network Analysis (Python)
  Data: snowball_example.xlsx
=============================================================
Outputs:
  figures/01_network_graph.png
  figures/02_degree_distribution.png
  figures/03_centrality_heatmap.png
  figures/04_level_composition.png
  figures/05_ego_networks_seeds.png
  figures/06_gender_age_breakdown.png
  figures/07_community_detection.png
  figures/08_summary_dashboard.png
"""

import os, warnings
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from collections import Counter

warnings.filterwarnings("ignore")

# ── Style ──────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0a0d14",
    "axes.facecolor":    "#111827",
    "axes.edgecolor":    "#2a3450",
    "axes.labelcolor":   "#e2e8f0",
    "xtick.color":       "#64748b",
    "ytick.color":       "#64748b",
    "text.color":        "#e2e8f0",
    "grid.color":        "#1c2333",
    "grid.linestyle":    "--",
    "grid.alpha":        0.6,
    "font.family":       "sans-serif",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "legend.framealpha": 0.3,
    "legend.facecolor":  "#1c2333",
    "legend.edgecolor":  "#2a3450",
})

LEVEL_COLORS = ["#f59e0b","#06b6d4","#3b82f6","#8b5cf6","#ec4899","#10b981"]
SEED_COLOR   = "#f59e0b"
NON_SEED_COLOR = "#6366f1"
GENDER_COLORS = {"Male": "#38bdf8", "Female": "#f472b6"}
AGE_COLORS    = {"Adult": "#a78bfa", "Minor": "#34d399"}

os.makedirs("figures", exist_ok=True)

# ═══════════════════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════════════════
print("📥  Loading data …")
nodes_df = pd.read_excel("snowball_example.xlsx", sheet_name="nodes")
edges_df  = pd.read_excel("snowball_example.xlsx", sheet_name="ties")

# Remove self-loops
edges_df = edges_df[edges_df["From"] != edges_df["To"]].reset_index(drop=True)

# Build directed graph
G = nx.DiGraph()
for _, row in nodes_df.iterrows():
    G.add_node(row["ID"], seed=row["Seed"], gender=row["Gender"],
               age=row["Age_Cat"], level=row["Level"])
for _, row in edges_df.iterrows():
    if row["From"] in G and row["To"] in G:
        G.add_edge(row["From"], row["To"])

G_und = G.to_undirected()   # undirected version for some metrics

print(f"   Nodes: {G.number_of_nodes()}  |  Edges: {G.number_of_edges()}")
print(f"   Seeds: {sum(1 for _,d in G.nodes(data=True) if d['seed']==1)}")
print(f"   Levels: {sorted(set(nx.get_node_attributes(G,'level').values()))}")

# ═══════════════════════════════════════════════════════════
# 2. CENTRALITY METRICS
# ═══════════════════════════════════════════════════════════
print("📐  Computing centrality …")
deg_cent    = nx.degree_centrality(G_und)
in_deg      = dict(G.in_degree())
out_deg     = dict(G.out_degree())
betw_cent   = nx.betweenness_centrality(G_und, normalized=True)
close_cent  = nx.closeness_centrality(G_und)
try:
    eigen_cent = nx.eigenvector_centrality(G_und, max_iter=1000)
except:
    eigen_cent = {n: 0 for n in G_und.nodes()}

# Attach to dataframe
nodes_df["degree"]      = nodes_df["ID"].map(lambda x: in_deg.get(x,0)+out_deg.get(x,0))
nodes_df["in_degree"]   = nodes_df["ID"].map(lambda x: in_deg.get(x,0))
nodes_df["out_degree"]  = nodes_df["ID"].map(lambda x: out_deg.get(x,0))
nodes_df["betweenness"] = nodes_df["ID"].map(betw_cent)
nodes_df["closeness"]   = nodes_df["ID"].map(close_cent)
nodes_df["eigenvector"] = nodes_df["ID"].map(eigen_cent)

# ═══════════════════════════════════════════════════════════
# FIGURE 1: NETWORK GRAPH
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 1 — Network graph …")
fig, ax = plt.subplots(figsize=(16, 11))
fig.patch.set_facecolor("#0a0d14")
ax.set_facecolor("#0a0d14")

# Layout — spring with seed nodes pushed to center
pos = nx.spring_layout(G_und, seed=42, k=1.8)

node_colors = [LEVEL_COLORS[G.nodes[n]["level"]] for n in G.nodes()]
node_sizes  = [250 + deg_cent[n]*2500 for n in G.nodes()]
seed_nodes  = [n for n,d in G.nodes(data=True) if d["seed"]==1]
non_seed_nodes = [n for n,d in G.nodes(data=True) if d["seed"]==0]

# Draw edges
nx.draw_networkx_edges(G_und, pos, ax=ax,
    edge_color="#6366f1", alpha=0.15, width=0.8, arrows=False)

# Draw non-seed nodes
nx.draw_networkx_nodes(G_und, pos, nodelist=non_seed_nodes, ax=ax,
    node_color=[LEVEL_COLORS[G.nodes[n]["level"]] for n in non_seed_nodes],
    node_size=[150 + deg_cent[n]*2000 for n in non_seed_nodes],
    alpha=0.75, linewidths=0)

# Draw seed nodes (larger, with gold ring)
nx.draw_networkx_nodes(G_und, pos, nodelist=seed_nodes, ax=ax,
    node_color=[LEVEL_COLORS[G.nodes[n]["level"]] for n in seed_nodes],
    node_size=[320 + deg_cent[n]*2800 for n in seed_nodes],
    alpha=0.95, edgecolors="#f59e0b", linewidths=2.5)

# Labels for seeds at level 0 only
seed0 = [n for n in seed_nodes if G.nodes[n]["level"] == 0]
nx.draw_networkx_labels(G_und, pos, labels={n:n for n in seed0}, ax=ax,
    font_size=6.5, font_color="#f59e0b", font_weight="bold")

# Legend
legend_els = [mpatches.Patch(facecolor=LEVEL_COLORS[lv],
              label=f"Level {lv}" + (" ★ Seeds" if lv==0 else ""))
              for lv in range(6)]
legend_els.append(mpatches.Patch(facecolor="none", edgecolor="#f59e0b",
                  linewidth=2, label="Seed node (ring)"))
ax.legend(handles=legend_els, loc="upper left", fontsize=8,
          title="Level Hierarchy", title_fontsize=9)

ax.set_title("Snowball Sampling — Social Network Graph\n"
             "Node size ∝ degree  ·  Gold ring = seed node  ·  Color = level",
             pad=16, fontsize=14)
ax.axis("off")
plt.tight_layout()
plt.savefig("figures/01_network_graph.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/01_network_graph.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 2: DEGREE DISTRIBUTION
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 2 — Degree distribution …")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Degree Distribution Analysis", fontsize=15, y=1.01)

for ax, (label, series) in zip(axes, [
    ("Total Degree", nodes_df["degree"]),
    ("In-Degree",    nodes_df["in_degree"]),
    ("Out-Degree",   nodes_df["out_degree"]),
]):
    counts = Counter(series)
    x = sorted(counts.keys())
    y = [counts[xi] for xi in x]

    ax.bar(x, y, color=LEVEL_COLORS[2], alpha=0.8, edgecolor="#3b82f6", linewidth=0.5)
    ax.axvline(series.mean(), color="#f59e0b", linestyle="--", lw=1.5,
               label=f"Mean={series.mean():.2f}")
    ax.axvline(series.median(), color="#ec4899", linestyle=":", lw=1.5,
               label=f"Median={series.median():.0f}")
    ax.set_title(label)
    ax.set_xlabel("Degree")
    ax.set_ylabel("Count")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y")

plt.tight_layout()
plt.savefig("figures/02_degree_distribution.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/02_degree_distribution.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 3: CENTRALITY HEATMAP (top 20 nodes)
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 3 — Centrality heatmap …")
cent_df = nodes_df[["ID","Level","Seed","degree","betweenness","closeness","eigenvector"]].copy()
cent_df["rank"] = cent_df["degree"] + cent_df["betweenness"] + cent_df["closeness"]
top20 = cent_df.nlargest(20, "rank").set_index("ID")

metrics = ["degree","betweenness","closeness","eigenvector"]
heat_data = top20[metrics].copy()
# Normalise each column 0-1
heat_data = (heat_data - heat_data.min()) / (heat_data.max() - heat_data.min() + 1e-9)

fig, ax = plt.subplots(figsize=(10, 9))
cmap = LinearSegmentedColormap.from_list("custom",
    ["#0a0d14", "#3b82f6", "#8b5cf6", "#f59e0b"])
im = ax.imshow(heat_data.values, cmap=cmap, aspect="auto", vmin=0, vmax=1)

ax.set_xticks(range(len(metrics)))
ax.set_xticklabels(["Degree","Betweenness","Closeness","Eigenvector"], fontsize=10)
ax.set_yticks(range(len(top20)))
# Colour ytick labels by seed status
ylabels = []
for node_id in top20.index:
    seed = top20.loc[node_id,"Seed"]
    level = int(top20.loc[node_id,"Level"])
    ylabels.append(f"{'★ ' if seed==1 else '  '}{node_id}  (Lv{level})")
ax.set_yticklabels(ylabels, fontsize=8)

# Seed node rows — gold left border
for i, node_id in enumerate(top20.index):
    if top20.loc[node_id,"Seed"] == 1:
        ax.add_patch(plt.Rectangle((-0.5, i-0.5), 0.08, 1,
            color="#f59e0b", transform=ax.transData, clip_on=False))

# Value annotations
for i in range(len(top20)):
    for j in range(len(metrics)):
        val = heat_data.values[i, j]
        ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                fontsize=7, color="white" if val < 0.7 else "#0a0d14")

plt.colorbar(im, ax=ax, fraction=0.03, label="Normalised Score")
ax.set_title("Centrality Heatmap — Top 20 Nodes\n★ = Seed node  |  Gold bar = seed",
             pad=14)
plt.tight_layout()
plt.savefig("figures/03_centrality_heatmap.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/03_centrality_heatmap.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 4: LEVEL COMPOSITION (stacked bars)
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 4 — Level composition …")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Level Composition by Seed · Gender · Age", fontsize=14)

# 4a — Seed vs Non-seed per level
lv_seed = nodes_df.groupby(["Level","Seed"]).size().unstack(fill_value=0)
lv_seed.columns = ["Non-seed","Seed"]
lv_seed.plot(kind="bar", ax=axes[0], color=[NON_SEED_COLOR, SEED_COLOR],
             edgecolor="#0a0d14", linewidth=0.5, alpha=0.9)
axes[0].set_title("Seed vs Non-seed per Level")
axes[0].set_xlabel("Level"); axes[0].set_ylabel("Count")
axes[0].legend(fontsize=9); axes[0].grid(True, axis="y")
for bar in axes[0].patches:
    h = bar.get_height()
    if h > 0:
        axes[0].text(bar.get_x()+bar.get_width()/2, h+0.2, int(h),
                     ha="center", va="bottom", fontsize=7, color="#e2e8f0")

# 4b — Gender per level
lv_gender = nodes_df.groupby(["Level","Gender"]).size().unstack(fill_value=0)
lv_gender.plot(kind="bar", ax=axes[1],
               color=[GENDER_COLORS["Female"], GENDER_COLORS["Male"]],
               edgecolor="#0a0d14", linewidth=0.5, alpha=0.9)
axes[1].set_title("Gender per Level")
axes[1].set_xlabel("Level"); axes[1].set_ylabel("Count")
axes[1].legend(fontsize=9); axes[1].grid(True, axis="y")

# 4c — Age per level
lv_age = nodes_df.groupby(["Level","Age_Cat"]).size().unstack(fill_value=0)
lv_age.plot(kind="bar", ax=axes[2],
            color=[AGE_COLORS["Adult"], AGE_COLORS["Minor"]],
            edgecolor="#0a0d14", linewidth=0.5, alpha=0.9)
axes[2].set_title("Age Category per Level")
axes[2].set_xlabel("Level"); axes[2].set_ylabel("Count")
axes[2].legend(fontsize=9); axes[2].grid(True, axis="y")

for ax in axes:
    ax.set_xticklabels([f"Lv{i}" for i in range(6)], rotation=0)

plt.tight_layout()
plt.savefig("figures/04_level_composition.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/04_level_composition.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 5: EGO NETWORKS OF TOP 4 SEED NODES (by degree)
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 5 — Ego networks of top seeds …")
seed_nodes_df = nodes_df[nodes_df["Seed"]==1].nlargest(4, "degree")
top_seeds = list(seed_nodes_df["ID"])

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Ego Networks — Top 4 Seed Nodes by Degree", fontsize=14, y=1.01)

for ax, seed_id in zip(axes.flat, top_seeds):
    ego = nx.ego_graph(G_und, seed_id, radius=1)
    epos = nx.spring_layout(ego, seed=7, k=2)

    ego_colors = []
    ego_sizes  = []
    ego_edges_color = []
    for n in ego.nodes():
        lv = G.nodes[n]["level"]
        ego_colors.append(LEVEL_COLORS[lv])
        ego_sizes.append(500 if n == seed_id else 200 + deg_cent[n]*800)

    nx.draw_networkx_edges(ego, epos, ax=ax, alpha=0.3,
                           edge_color="#6366f1", width=1.2)
    nx.draw_networkx_nodes(ego, epos, ax=ax,
                           node_color=ego_colors, node_size=ego_sizes,
                           edgecolors=["#f59e0b" if n==seed_id else "#1c2333" for n in ego.nodes()],
                           linewidths=[3 if n==seed_id else 0.5 for n in ego.nodes()])
    nx.draw_networkx_labels(ego, epos, ax=ax, font_size=7,
                            font_color="#e2e8f0")

    row = nodes_df[nodes_df["ID"]==seed_id].iloc[0]
    ax.set_title(
        f"{seed_id} — Lv{row.Level}  {row.Gender} / {row.Age_Cat}\n"
        f"Degree={row.degree}  Betweenness={row.betweenness:.3f}",
        fontsize=9)
    ax.axis("off")

plt.tight_layout()
plt.savefig("figures/05_ego_networks_seeds.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/05_ego_networks_seeds.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 6: GENDER & AGE BREAKDOWN (pie + violin)
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 6 — Gender & age breakdown …")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Node Attribute Analysis", fontsize=14)

# Donut — gender
g_counts = nodes_df["Gender"].value_counts()
axes[0].pie(g_counts, labels=g_counts.index, autopct="%1.0f%%",
            colors=[GENDER_COLORS[g] for g in g_counts.index],
            startangle=90, wedgeprops={"width":0.55, "edgecolor":"#0a0d14","linewidth":2},
            textprops={"color":"#e2e8f0","fontsize":11})
axes[0].set_title("Gender Split")

# Donut — age
a_counts = nodes_df["Age_Cat"].value_counts()
axes[1].pie(a_counts, labels=a_counts.index, autopct="%1.0f%%",
            colors=[AGE_COLORS[a] for a in a_counts.index],
            startangle=90, wedgeprops={"width":0.55, "edgecolor":"#0a0d14","linewidth":2},
            textprops={"color":"#e2e8f0","fontsize":11})
axes[1].set_title("Age Category Split")

# Violin — degree by level
level_degree = [(d["level"], nodes_df.loc[nodes_df["ID"]==n,"degree"].values[0])
                for n,d in G.nodes(data=True)]
lv_df = pd.DataFrame(level_degree, columns=["Level","Degree"])
vp = axes[2].violinplot([lv_df[lv_df["Level"]==lv]["Degree"].tolist() for lv in range(6)],
                         positions=range(6), showmedians=True, showmeans=False)
for i, body in enumerate(vp["bodies"]):
    body.set_facecolor(LEVEL_COLORS[i])
    body.set_alpha(0.7)
vp["cmedians"].set_color("#f59e0b")
vp["cmedians"].set_linewidth(2)
for part in ["cbars","cmins","cmaxes"]:
    vp[part].set_color("#2a3450")
axes[2].set_xticks(range(6))
axes[2].set_xticklabels([f"Lv{i}" for i in range(6)])
axes[2].set_title("Degree Distribution per Level")
axes[2].set_xlabel("Level"); axes[2].set_ylabel("Degree")
axes[2].grid(True, axis="y")

plt.tight_layout()
plt.savefig("figures/06_gender_age_breakdown.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/06_gender_age_breakdown.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 7: COMMUNITY DETECTION (Louvain / Greedy Modularity)
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 7 — Community detection …")
communities = list(nx.community.greedy_modularity_communities(G_und))
modularity  = nx.community.modularity(G_und, communities)
n_comm      = len(communities)
print(f"   Communities: {n_comm}  |  Modularity: {modularity:.4f}")

comm_colors = plt.cm.tab20.colors
node_comm   = {}
for i, comm in enumerate(communities):
    for node in comm:
        node_comm[node] = i

fig, ax = plt.subplots(figsize=(16, 11))
fig.patch.set_facecolor("#0a0d14")
ax.set_facecolor("#0a0d14")

pos2 = nx.spring_layout(G_und, seed=99, k=2.0)
comm_node_colors = [comm_colors[node_comm[n] % 20] for n in G_und.nodes()]
node_sizes2 = [200 + deg_cent[n]*2000 for n in G_und.nodes()]

nx.draw_networkx_edges(G_und, pos2, ax=ax,
    edge_color="#334155", alpha=0.2, width=0.8)
nx.draw_networkx_nodes(G_und, pos2, ax=ax,
    node_color=comm_node_colors, node_size=node_sizes2,
    edgecolors=["#f59e0b" if G.nodes[n]["seed"]==1 else "none" for n in G_und.nodes()],
    linewidths=[2 if G.nodes[n]["seed"]==1 else 0 for n in G_und.nodes()],
    alpha=0.9)

# Community labels (centroid)
for i, comm in enumerate(communities):
    if len(comm) < 2: continue
    cx = np.mean([pos2[n][0] for n in comm])
    cy = np.mean([pos2[n][1] for n in comm])
    ax.text(cx, cy, f"C{i+1}\n({len(comm)})",
            ha="center", va="center", fontsize=8,
            color="white", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=comm_colors[i%20],
                      alpha=0.6, edgecolor="none"))

ax.set_title(f"Community Detection — Greedy Modularity\n"
             f"{n_comm} communities  |  Modularity = {modularity:.4f}  |  Gold ring = seed",
             pad=16, fontsize=13)
ax.axis("off")
plt.tight_layout()
plt.savefig("figures/07_community_detection.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/07_community_detection.png")

# ═══════════════════════════════════════════════════════════
# FIGURE 8: SUMMARY DASHBOARD
# ═══════════════════════════════════════════════════════════
print("🎨  Fig 8 — Summary dashboard …")
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#0a0d14")
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.38)

# ── A: Key metrics text panel ──────────────────────────────
ax_metrics = fig.add_subplot(gs[0, :2])
ax_metrics.set_facecolor("#111827")
ax_metrics.set_xlim(0,1); ax_metrics.set_ylim(0,1); ax_metrics.axis("off")

density_val = nx.density(G_und)
clust_val   = nx.average_clustering(G_und)
try:
    avg_path = nx.average_shortest_path_length(G_und)
except:
    # Graph not connected; use largest component
    lcc = G_und.subgraph(max(nx.connected_components(G_und), key=len))
    avg_path = nx.average_shortest_path_length(lcc)
    avg_path_note = " (LCC)"
else:
    avg_path_note = ""

metrics_text = [
    ("Nodes",          str(G.number_of_nodes()),    "#06b6d4"),
    ("Edges",          str(G.number_of_edges()),    "#3b82f6"),
    ("Seeds",          str(sum(1 for _,d in G.nodes(data=True) if d["seed"]==1)), "#f59e0b"),
    ("Levels",         "6",                         "#8b5cf6"),
    ("Density",        f"{density_val:.4f}",        "#ec4899"),
    ("Avg. Clustering",f"{clust_val:.4f}",          "#10b981"),
    ("Avg. Path Len",  f"{avg_path:.2f}{avg_path_note}", "#f59e0b"),
    ("Components",     str(nx.number_connected_components(G_und)), "#06b6d4"),
    ("Communities",    str(n_comm),                 "#8b5cf6"),
    ("Modularity",     f"{modularity:.4f}",         "#ec4899"),
]

cols = 2; rows = 5
for idx, (lbl, val, color) in enumerate(metrics_text):
    c = idx % cols;  r = idx // cols
    x = 0.05 + c * 0.5;  y = 0.88 - r * 0.18
    ax_metrics.text(x, y,   val, fontsize=20, fontweight="bold", color=color,
                    transform=ax_metrics.transAxes)
    ax_metrics.text(x, y-0.08, lbl, fontsize=8, color="#64748b",
                    transform=ax_metrics.transAxes)

ax_metrics.set_title("📊  Network Summary Statistics", fontsize=12, pad=8)

# ── B: Degree distribution bars ────────────────────────────
ax_deg = fig.add_subplot(gs[0, 2:])
deg_counts = Counter(nodes_df["degree"])
bars = ax_deg.bar(sorted(deg_counts), [deg_counts[k] for k in sorted(deg_counts)],
                  color=LEVEL_COLORS[2], alpha=0.85, edgecolor="#1c2333")
ax_deg.set_title("Degree Distribution"); ax_deg.set_xlabel("Degree"); ax_deg.set_ylabel("Count")
ax_deg.axvline(nodes_df["degree"].mean(), color="#f59e0b", lw=1.5, ls="--",
               label=f"Mean={nodes_df['degree'].mean():.1f}")
ax_deg.legend(fontsize=8); ax_deg.grid(True, axis="y")

# ── C: Nodes per level (horizontal bars) ───────────────────
ax_lv = fig.add_subplot(gs[1, :2])
lv_cnt = nodes_df["Level"].value_counts().sort_index()
ax_lv.barh([f"Level {i}" for i in lv_cnt.index], lv_cnt.values,
           color=[LEVEL_COLORS[i] for i in lv_cnt.index], alpha=0.9)
ax_lv.set_title("Nodes per Level"); ax_lv.set_xlabel("Count")
for i, v in enumerate(lv_cnt.values):
    ax_lv.text(v+0.2, i, str(v), va="center", fontsize=9)
ax_lv.grid(True, axis="x")

# ── D: Seed vs non-seed per level ──────────────────────────
ax_sd = fig.add_subplot(gs[1, 2:])
lv_sd = nodes_df.groupby(["Level","Seed"]).size().unstack(fill_value=0)
lv_sd.columns = ["Non-seed","Seed"]
lv_sd.plot(kind="bar", ax=ax_sd, color=[NON_SEED_COLOR, SEED_COLOR],
           edgecolor="#0a0d14", alpha=0.9, legend=True)
ax_sd.set_title("Seed vs Non-seed per Level")
ax_sd.set_xlabel("Level"); ax_sd.set_ylabel("Count")
ax_sd.set_xticklabels([f"Lv{i}" for i in range(6)], rotation=0)
ax_sd.grid(True, axis="y"); ax_sd.legend(fontsize=8)

# ── E: Top 10 nodes by betweenness ─────────────────────────
ax_btw = fig.add_subplot(gs[2, :2])
top10_btw = nodes_df.nlargest(10, "betweenness")[["ID","betweenness","Level","Seed"]]
colors_btw = [LEVEL_COLORS[int(lv)] for lv in top10_btw["Level"]]
bars2 = ax_btw.barh(top10_btw["ID"], top10_btw["betweenness"],
                    color=colors_btw, alpha=0.9)
# Gold outline for seeds
for bar, (_, row) in zip(bars2, top10_btw.iterrows()):
    if row["Seed"] == 1:
        bar.set_edgecolor("#f59e0b"); bar.set_linewidth(2)
ax_btw.set_title("Top 10 Nodes — Betweenness Centrality\n(gold outline = seed)")
ax_btw.set_xlabel("Betweenness Centrality")
ax_btw.invert_yaxis(); ax_btw.grid(True, axis="x")

# ── F: Closeness vs Degree scatter ─────────────────────────
ax_sc = fig.add_subplot(gs[2, 2:])
scatter_colors = [LEVEL_COLORS[lv] for lv in nodes_df["Level"]]
scatter_sizes  = [120 if s==1 else 50 for s in nodes_df["Seed"]]
ax_sc.scatter(nodes_df["degree"], nodes_df["closeness"],
              c=scatter_colors, s=scatter_sizes, alpha=0.75,
              edgecolors=["#f59e0b" if s==1 else "none" for s in nodes_df["Seed"]],
              linewidths=1.5)
ax_sc.set_title("Degree vs Closeness Centrality\n(size/outline = seed)")
ax_sc.set_xlabel("Degree"); ax_sc.set_ylabel("Closeness Centrality")
ax_sc.grid(True)
legend_patches = [mpatches.Patch(facecolor=LEVEL_COLORS[lv], label=f"Level {lv}")
                  for lv in range(6)]
ax_sc.legend(handles=legend_patches, fontsize=7, ncol=3)

fig.suptitle("⬡  Snowball Network Analysis — Summary Dashboard",
             fontsize=16, fontweight="bold", y=1.01,
             color="#e2e8f0")
plt.savefig("figures/08_summary_dashboard.png", dpi=150, bbox_inches="tight",
            facecolor="#0a0d14")
plt.close()
print("   ✓ figures/08_summary_dashboard.png")

# ═══════════════════════════════════════════════════════════
# PRINT SUMMARY TABLE
# ═══════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  SNOWBALL SNA — KEY RESULTS")
print("═"*60)
print(f"  Nodes          : {G.number_of_nodes()}")
print(f"  Edges          : {G.number_of_edges()}")
print(f"  Seeds          : {sum(1 for _,d in G.nodes(data=True) if d['seed']==1)}")
print(f"  Levels         : 0–5")
print(f"  Density        : {density_val:.5f}")
print(f"  Avg Clustering : {clust_val:.4f}")
print(f"  Avg Path Len   : {avg_path:.3f}{avg_path_note}")
print(f"  Components     : {nx.number_connected_components(G_und)}")
print(f"  Communities    : {n_comm}  (Modularity={modularity:.4f})")
print()
print("  Top 5 nodes by BETWEENNESS:")
for _, r in nodes_df.nlargest(5,"betweenness")[["ID","Level","Seed","degree","betweenness"]].iterrows():
    star = "★" if r.Seed==1 else " "
    print(f"    {star} {r.ID:>4}  Lv{r.Level}  deg={r.degree}  btw={r.betweenness:.4f}")
print()
print("  Top 5 nodes by DEGREE:")
for _, r in nodes_df.nlargest(5,"degree")[["ID","Level","Seed","degree","betweenness"]].iterrows():
    star = "★" if r.Seed==1 else " "
    print(f"    {star} {r.ID:>4}  Lv{r.Level}  deg={r.degree}  btw={r.betweenness:.4f}")
print("═"*60)
print("\n✅  All 8 figures saved to the 'figures/' folder.")
