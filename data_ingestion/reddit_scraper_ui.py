import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from pymongo import MongoClient
import certifi

# =========================
# CONFIG
# =========================

SEARCH_URL = "https://www.reddit.com/search/?q=caf+morocco&type=posts&sort=new"

POST_LINK_SELECTOR = "search-telemetry-tracker h2 a"

POST_AUTHOR_XPATH = "/html/body/shreddit-app/div[3]/div/div/main/shreddit-post/div[1]/span[1]/div/div/span/div/faceplate-hovercard/faceplate-tracker/a"

SCROLL_PAUSE = 2
MAX_SCROLLS = 8

# =========================
# MONGODB
# =========================

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["EFMBIGDATA"]
collection = db["reddit_ui_posts_clean"]

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


def extract_post_author(page):
    XPATHS = [
        "/html/body/shreddit-app/div[3]/div/div/main/"
        "shreddit-post/div[1]/span[1]/div/div/span/div/"
        "faceplate-hovercard/faceplate-tracker/a",

        "/html/body/shreddit-app/div[3]/div/div/main/"
        "shreddit-post/div[1]/span[1]/div/div/span/div/"
        "faceplate-tracker/a"
    ]

    for xpath in XPATHS:
        try:
            # 🔥 wait for this specific variant
            page.wait_for_selector(
                f"xpath={xpath}",
                timeout=6000
            )

            locator = page.locator(f"xpath={xpath}")
            if locator.count() > 0:
                author = locator.first.inner_text().strip()
                if author:
                    return author

        except:
            pass

    print("⚠️ Post author not found with any XPath → deleted")
    time.sleep(30)
    return "deleted"




def extract_author_and_text(raw_text):
    if not raw_text:
        return None, None

    # Username is always before the bullet
    parts = raw_text.split("\n•", 1)
    author = parts[0].strip()

    # Comment body starts after empty line
    body = raw_text
    if "\n\n" in raw_text:
        body = raw_text.split("\n\n", 1)[1].strip()

    return author, body


def extract_comments(comment_element, depth=0):
    comments = []

    try:
        raw_text = comment_element.inner_text(timeout=2000).strip()
        author, body = extract_author_and_text(raw_text)

        if author and body:
            comments.append({
                "author": author,
                "text": body,
                "depth": depth
            })

            print(f"{'  ' * depth}🗨️ {author}: {body[:80]}")

        replies = comment_element.locator(":scope > shreddit-comment")
        for i in range(replies.count()):
            comments.extend(
                extract_comments(replies.nth(i), depth + 1)
            )

    except Exception as e:
        print("⚠️ Comment extraction failed:", e)

    return comments


def scrape_post(page):
    time.sleep(2)
    scroll_until_loaded(page, 6)

    title = page.locator("h1").first.inner_text()
    post_author = extract_post_author(page)

    print(f"\n📝 POST: {title}")
    print(f"👤 POST AUTHOR: {post_author}")

    comments = []
    comment_tree = page.locator("shreddit-comment-tree > shreddit-comment")

    print(f"💬 Top-level comments: {comment_tree.count()}")

    for i in range(comment_tree.count()):
        comments.extend(
            extract_comments(comment_tree.nth(i))
        )

    print(f"✅ Total comments extracted: {len(comments)}")

    return {
        "title": title,
        "author": post_author,
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

        page = context.new_page()
        page.goto(SEARCH_URL)
        time.sleep(10)
        page.wait_for_load_state("networkidle")

        print("✅ Search page loaded")

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
            print("✅ Post page loaded:", post_url)

            post_data = scrape_post(page)

            document = {
                "search_url": SEARCH_URL,
                "post_url": post_url,
                "scraped_at": datetime.utcnow(),
                **post_data
            }

            collection.insert_one(document)
            print("📦 Inserted into MongoDB")

            page.go_back()
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            post_index += 1

        browser.close()
        print("\n🎯 Scraping completed")


if __name__ == "__main__":
    main()
