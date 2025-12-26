import networkx as nx
from pymongo import MongoClient
import certifi
import community as community_louvain  # python-louvain

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

BAD_USERS = {None, "", "deleted", "[deleted]", "[supprimé]", "AutoModerator"}

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client["EFMBIGDATA"]
edges_col = db["reddit_edges"]
communities_col = db["reddit_user_communities"]

communities_col.delete_many({})
print("🧹 Cleared old communities")

# Build an UNDIRECTED graph for Louvain (standard practice)
G = nx.Graph()

for e in edges_col.find({}, {"source": 1, "target": 1}):
    s = e.get("source")
    t = e.get("target")
    if s in BAD_USERS or t in BAD_USERS or s == t:
        continue
    # accumulate weight if repeated
    if G.has_edge(s, t):
        G[s][t]["weight"] += 1
    else:
        G.add_edge(s, t, weight=1)

print(f"✅ Community graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Louvain partition
partition = community_louvain.best_partition(G, weight="weight")

# Save to MongoDB
for user, community_id in partition.items():
    communities_col.insert_one({
        "user": user,
        "community": int(community_id)
    })

# Print community sizes
from collections import Counter
sizes = Counter(partition.values())
print("\n🏘️ Top communities by size:")
for cid, size in sizes.most_common(10):
    print(f"Community {cid}: {size} users")

print("\n📦 Communities stored in MongoDB (reddit_user_communities)")
