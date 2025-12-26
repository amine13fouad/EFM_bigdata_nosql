from pymongo import MongoClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import certifi

# =========================
# MONGODB CONFIG
# =========================

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["EFMBIGDATA"]
posts_col = db["reddit_ui_posts_clean"]
sent_col = db["reddit_sentiment"]

# =========================
# SENTIMENT SETUP
# =========================

analyzer = SentimentIntensityAnalyzer()

def label_from_compound(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"

sent_col.delete_many({})
print("🧹 Cleared reddit_sentiment")

count = 0

# =========================
# PROCESS POSTS
# =========================

for post in posts_col.find({}, {"post_url": 1, "title": 1, "comments": 1, "scraped_at": 1}):
    post_url = post.get("post_url")
    scraped_at = post.get("scraped_at")
    title = post.get("title", "")

    # ---- Post-level sentiment (title)
    title_score = analyzer.polarity_scores(title)
    sent_col.insert_one({
        "post_url": post_url,
        "scraped_at": scraped_at,
        "level": "post",
        "text": title,
        "compound": title_score["compound"],
        "label": label_from_compound(title_score["compound"])
    })
    count += 1

    # ---- Comment-level sentiment
    for c in post.get("comments", []):
        text = c.get("text", "")
        author = c.get("author")

        score = analyzer.polarity_scores(text)
        sent_col.insert_one({
            "post_url": post_url,
            "scraped_at": scraped_at,
            "level": "comment",
            "author": author,
            "text": text,
            "compound": score["compound"],
            "label": label_from_compound(score["compound"])
        })
        count += 1

print(f"✅ Inserted {count} sentiment documents into reddit_sentiment")
