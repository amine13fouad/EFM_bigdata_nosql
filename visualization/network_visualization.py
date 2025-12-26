import networkx as nx
import matplotlib.pyplot as plt
from pymongo import MongoClient
import certifi

# =========================
# CONFIG
# =========================

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

TOP_USERS = 120   # adjust if needed (80–150 works well)

# =========================
# LOAD DATA
# =========================

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client["EFMBIGDATA"]

edges_col = db["reddit_edges"]
metrics_col = db["reddit_user_metrics"]
comm_col = db["reddit_user_communities"]

# -------------------------
# Load metrics
# -------------------------
metrics = {}
for m in metrics_col.find({}, {"user": 1, "weighted_in_degree": 1}):
    metrics[m["user"]] = m.get("weighted_in_degree", 1)

# Select top influential users
top_users = sorted(metrics, key=metrics.get, reverse=True)[:TOP_USERS]
top_users = set(top_users)

# -------------------------
# Load communities
# -------------------------
communities = {}
for c in comm_col.find({}, {"user": 1, "community": 1}):
    communities[c["user"]] = c["community"]

# =========================
# BUILD SUBGRAPH
# =========================

G = nx.DiGraph()

for e in edges_col.find({}, {"source": 1, "target": 1}):
    s = e["source"]
    t = e["target"]

    if s in top_users and t in top_users:
        G.add_edge(s, t)

print(f"Graph for visualization: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# =========================
# VISUALIZATION
# =========================

plt.figure(figsize=(16, 16))

pos = nx.spring_layout(G, seed=42, k=0.35)

# Node sizes = influence
node_sizes = [
    metrics.get(n, 1) * 40 for n in G.nodes()
]

# Node colors = community
node_colors = [
    communities.get(n, 0) for n in G.nodes()
]

nodes = nx.draw_networkx_nodes(
    G,
    pos,
    node_size=node_sizes,
    node_color=node_colors,
    cmap=plt.cm.tab20,
    alpha=0.85
)

nx.draw_networkx_edges(
    G,
    pos,
    alpha=0.25,
    arrows=False
)

# Label only top 15 users (readable)
top_15 = sorted(metrics, key=metrics.get, reverse=True)[:15]

labels = {u: u for u in top_15 if u in G.nodes()}

nx.draw_networkx_labels(
    G,
    pos,
    labels,
    font_size=9,
    font_weight="bold"
)

plt.title(
    "Reddit Interaction Network\n"
    "Node size = influence (weighted in-degree), color = community",
    fontsize=14
)

plt.axis("off")
plt.tight_layout()
plt.show()
