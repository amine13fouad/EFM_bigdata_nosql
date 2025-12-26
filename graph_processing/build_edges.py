from pymongo import MongoClient
from datetime import datetime
import certifi

# =========================
# CONFIG
# =========================

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

BAD_USERS = {
    None, "", "deleted", "[deleted]", "[supprimé]", "AutoModerator"
}

# =========================
# MONGODB
# =========================

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["EFMBIGDATA"]
posts_col = db["reddit_ui_posts_clean"]
edges_col = db["reddit_edges"]

edges_col.delete_many({})
print("🧹 reddit_edges cleared")

edge_count_case1 = 0
edge_count_case2 = 0

# =========================
# EDGE CREATION
# =========================

for post in posts_col.find():
    post_author = post.get("author")
    post_url = post.get("post_url")

    comments = post.get("comments", [])

    # -----------------
    # CASE 1: comment → post author
    # -----------------
    if post_author not in BAD_USERS:
        for c in comments:
            ca = c.get("author")
            if ca in BAD_USERS or ca == post_author:
                continue

            edges_col.insert_one({
                "source": ca,
                "target": post_author,
                "post_url": post_url,
                "interaction": "comment_on_post",
                "created_at": datetime.utcnow()
            })
            edge_count_case1 += 1

    # -----------------
    # CASE 2: reply → parent comment
    # -----------------
    last_by_depth = {}

    for c in comments:
        author = c.get("author")
        depth = c.get("depth")

        if author in BAD_USERS:
            continue

        # If this is a reply (depth > 0)
        if depth > 0 and (depth - 1) in last_by_depth:
            parent_author = last_by_depth[depth - 1]

            if parent_author not in BAD_USERS and parent_author != author:
                edges_col.insert_one({
                    "source": author,
                    "target": parent_author,
                    "post_url": post_url,
                    "interaction": "reply_to_comment",
                    "created_at": datetime.utcnow()
                })
                edge_count_case2 += 1

        # Update stack
        last_by_depth[depth] = author

print("\n✅ EDGE CREATION FINISHED")
print(f"   • Case 1 edges: {edge_count_case1}")
print(f"   • Case 2 edges: {edge_count_case2}")
print(f"   • TOTAL edges: {edge_count_case1 + edge_count_case2}")
