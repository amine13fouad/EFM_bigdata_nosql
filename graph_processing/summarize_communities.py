from pymongo import MongoClient
import certifi
from collections import defaultdict

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client["EFMBIGDATA"]

metrics_col = db["reddit_user_metrics"]          # has weighted_in_degree, weighted_out_degree, betweenness
comm_col = db["reddit_user_communities"]         # has user, community
summary_col = db["reddit_community_summary"]

summary_col.delete_many({})
print("🧹 Cleared old reddit_community_summary")

# Load community mapping
user_to_comm = {}
for doc in comm_col.find({}, {"user": 1, "community": 1}):
    user_to_comm[doc["user"]] = doc["community"]

# Group users by community with metrics
community_users = defaultdict(list)

for m in metrics_col.find({}, {"user": 1, "weighted_in_degree": 1, "weighted_out_degree": 1, "betweenness": 1}):
    u = m["user"]
    if u not in user_to_comm:
        continue
    cid = user_to_comm[u]
    community_users[cid].append({
        "user": u,
        "weighted_in_degree": m.get("weighted_in_degree", 0),
        "weighted_out_degree": m.get("weighted_out_degree", 0),
        "betweenness": m.get("betweenness", 0.0),
    })

# Build summary per community
for cid, users in community_users.items():
    users_sorted_in = sorted(users, key=lambda x: x["weighted_in_degree"], reverse=True)
    users_sorted_bt = sorted(users, key=lambda x: x["betweenness"], reverse=True)

    doc = {
        "community": int(cid),
        "size": len(users),
        "top_influential": users_sorted_in[:5],
        "top_bridges": users_sorted_bt[:5],
    }
    summary_col.insert_one(doc)

# Print top 10 communities by size + their top users
top_comms = sorted(community_users.items(), key=lambda kv: len(kv[1]), reverse=True)[:10]

print("\n🏘️ Community summaries (top 10 by size):")
for cid, users in top_comms:
    print(f"\nCommunity {cid} | size={len(users)}")
    print("  Top influential (weighted_in_degree):")
    for u in sorted(users, key=lambda x: x["weighted_in_degree"], reverse=True)[:5]:
        print(f"   - {u['user']}: {u['weighted_in_degree']}")
    print("  Top bridges (betweenness):")
    for u in sorted(users, key=lambda x: x["betweenness"], reverse=True)[:5]:
        print(f"   - {u['user']}: {u['betweenness']:.6f}")

print("\n📦 Saved summaries to reddit_community_summary")
