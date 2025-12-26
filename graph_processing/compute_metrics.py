import networkx as nx
from pymongo import MongoClient
import certifi

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

BAD_USERS = {
    None, "", "deleted", "[deleted]", "[supprimé]", "AutoModerator"
}

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client["EFMBIGDATA"]
edges_col = db["reddit_edges"]
metrics_col = db["reddit_user_metrics"]

metrics_col.delete_many({})
print("🧹 Cleared old metrics")

# Build weighted directed graph
G = nx.DiGraph()
edge_counter = {}

for e in edges_col.find({}, {"source": 1, "target": 1}):
    s = e.get("source")
    t = e.get("target")
    if s in BAD_USERS or t in BAD_USERS:
        continue
    if s == t:
        continue
    edge_counter[(s, t)] = edge_counter.get((s, t), 0) + 1

for (s, t), w in edge_counter.items():
    G.add_edge(s, t, weight=w)

print(f"✅ Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} unique edges")

# Weighted degrees
weighted_out = {n: 0 for n in G.nodes()}
weighted_in = {n: 0 for n in G.nodes()}
for u, v, d in G.edges(data=True):
    w = d.get("weight", 1)
    weighted_out[u] += w
    weighted_in[v] += w

# Betweenness (will still be low with Case 1-only graph)
betweenness = nx.betweenness_centrality(G, normalized=True)

# Store
for user in G.nodes():
    metrics_col.insert_one({
        "user": user,
        "weighted_in_degree": weighted_in.get(user, 0),
        "weighted_out_degree": weighted_out.get(user, 0),
        "betweenness": betweenness.get(user, 0.0)
    })

print("📦 Metrics stored in MongoDB")

print("\n🏆 Top 10 Influential (weighted in-degree):")
for u, s in sorted(weighted_in.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(u, s)

print("\n🔥 Top 10 Active (weighted out-degree):")
for u, s in sorted(weighted_out.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(u, s)

print("\n🌉 Top 10 Bridge (betweenness):")
for u, s in sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(u, round(s, 6))
