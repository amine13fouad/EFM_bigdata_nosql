import json
import time
from datetime import datetime
from pymongo import MongoClient
from playwright.sync_api import sync_playwright

# =========================
# CONFIG
# =========================

SEARCH_URL = "https://www.reddit.com/search/?q=caf+morocco&type=posts&sort=new"
COOKIE_PATH = "cookies.json"

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"
DB_NAME = "EFMBIGDATA"
COLLECTION_NAME = "reddit_posts"

POST_LINK_SELECTOR = "search-telemetry-tracker h2 a"
SCROLL_PAUSE = 2
MAX_SCROLLS = 10


# =========================
# MONGODB
# =========================

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# =========================
# COOKIES
# =========================

def load_cookies(context):
    with open(COOKIE_PATH, "r") as f:
        cookies = json.load(f)

    formatted = []
    for c in cookies:
        cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
            "sameSite": "Lax"
        }

        if "expirationDate" in c:
            cookie["expires"] = int(c["expirationDate"])

        if c.get("sameSite") == "no_restriction":
            cookie["sameSite"] = "None"
        elif c.get("sameSite"):
            cookie["sameSite"] = c["sameSite"].capitalize()

        formatted.append(cookie)

    context.add_cookies(formatted)
    print(f"✅ Loaded {len(formatted)} cookies")


# =========================
# UTILS
# =========================

def scroll_until_loaded(page, max_scrolls=MAX_SCROLLS):
    last_height = page.evaluate("document.body.scrollHeight")
    for _ in range(max_scrolls):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(SCROLL_PAUSE)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_comments(comment_element, depth=0):
    comments = []

    try:
        text = comment_element.inner_text(timeout=2000).strip()
        if text:
            print(f"{'  ' * depth}🗨️ Comment (depth={depth})")
            comments.append({
                "depth": depth,
                "text": text
            })

        replies = comment_element.locator(":scope > shreddit-comment")
        for i in range(replies.count()):
            comments.extend(
                extract_comments(replies.nth(i), depth + 1)
            )

    except Exception as e:
        print(f"⚠️ Comment extraction failed: {e}")

    return comments


def scrape_post(page):
    time.sleep(2)
    scroll_until_loaded(page, 6)

    title = page.locator("h1").first.inner_text()
    print(f"\n📝 POST: {title}")

    try:
        content = page.locator("div[data-testid='post-container']").inner_text()
    except:
        content = ""

    comments = []
    top_comments = page.locator("shreddit-comment-tree > shreddit-comment")
    print(f"💬 Top-level comments: {top_comments.count()}")

    for i in range(top_comments.count()):
        comments.extend(
            extract_comments(top_comments.nth(i))
        )

    print(f"✅ Total comments extracted: {len(comments)}")

    return {
        "title": title,
        "content": content,
        "comments": comments,
        "comment_count": len(comments)
    }


# =========================
# MAIN
# =========================

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            )
        )

        # 🔥 LOAD COOKIES FIRST
        load_cookies(context)

        page = context.new_page()
        page.goto(f"{SEARCH_URL}")
        time.sleep(10)
        #page.wait_for_load_state("networkidle")

        print("✅ Reddit search page loaded")

        post_index = 0

        while True:
            scroll_until_loaded(page)

            posts = page.locator(POST_LINK_SELECTOR)
            if post_index >= posts.count():
                break

            post_url = posts.nth(post_index).get_attribute("href")
            if not post_url:
                post_index += 1
                continue

            print(f"\n🔹 Opening post {post_index + 1}")
            page.goto(f"https://www.reddit.com/{post_url}")
            print(f"✅ Post page loaded: {post_url}")
            # In case of captcha showing up
            time.sleep(10)

            post_data = scrape_post(page)

            # 🔥 INSERT INTO MONGODB
            document = {
                "search_url": SEARCH_URL,
                "post_url": post_url,
                "scraped_at": datetime.utcnow(),
                **post_data
            }

            collection.insert_one(document)
            print("📦 Inserted into MongoDB")

            page.go_back()
            #page.wait_for_load_state("networkidle")
            time.sleep(10)
            time.sleep(2)

            post_index += 1

        browser.close()
        print("\n🎯 Scraping finished")


if __name__ == "__main__":
    main()
