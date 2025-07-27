import os
import json
import feedparser
import requests
import re

DATA_FILE = "data.json"
RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxnxya_32jcKj4yN1_kD7A"  # Muse Indonesia

# 💾 ───── Handling ID Storage ─────
def load_sent_post_ids():
    return _load_json_field("sent_post_ids", warn="data.json belum ada.")

def save_sent_post_ids(post_ids):
    _save_json_field("sent_post_ids", post_ids, "sent_post_ids")

def load_sent_video_ids():
    return _load_json_field("sent_video_ids", warn="data.json belum ada untuk video.")

def save_sent_video_ids(video_ids):
    _save_json_field("sent_video_ids", video_ids, "sent_video_ids")

def _load_json_field(field, warn="data.json belum ada."):
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return data.get(field, [])
        else:
            print("[LOAD]", warn)
            return []
    except Exception as e:
        print(f"[ERROR] load_{field}: {e}")
        return []

def _save_json_field(field, value, label):
    try:
        data = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        data[field] = value
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[SAVE] {label}: {len(value)} disimpan")
    except Exception as e:
        print(f"[ERROR] save_{field}: {e}")

# 🔍 ───── Scraper Komunitas ─────
def get_latest_posts(channel_url, max_posts=5):
    results = []
    try:
        response = requests.get(channel_url + "/community", headers={"User-Agent": "Mozilla/5.0"})
        html = response.text
        match = re.search(r"var ytInitialData = ({.*?});</script>", html)
        if not match:
            print("[ERROR] ytInitialData tidak ditemukan.")
            return []

        data = json.loads(match.group(1))
        tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
        for tab in tabs:
            tab_renderer = tab.get("tabRenderer", {})
            if "content" not in tab_renderer:
                continue

            sections = tab_renderer["content"].get("sectionListRenderer", {}).get("contents", [])
            for section in sections:
                posts = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in posts:
                    try:
                        post_data = item["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]
                        post_id = post_data.get("postId")
                        if not post_id or not post_id.startswith("Ugk"):
                            continue
                        text_runs = post_data.get("contentText", {}).get("runs", [])
                        text = "".join(run.get("text", "") for run in text_runs).strip()
                        timestamp = post_data.get("publishedTimeText", {}).get("runs", [{}])[0].get("text", "")
                        results.append({
                            "id": post_id,
                            "url": f"https://www.youtube.com/post/{post_id}",
                            "text": text,
                            "timestamp": timestamp
                        })
                        if len(results) >= max_posts:
                            return results
                    except KeyError:
                        continue
    except Exception as e:
        print(f"[ERROR] Gagal scrape komunitas: {e}")
    return results

# 🔍 ───── Scraper Video via RSS (filter ID) ─────
def get_latest_rss_videos(rss_url=RSS_URL, max_items=3, include_sent=False):
    results = []
    try:
        sent_ids = load_sent_video_ids()
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            video_id = entry.yt_videoid
            if not include_sent and video_id in sent_ids:
                continue
            results.append({
                "id": video_id,
                "title": entry.title,
                "url": entry.link,
                "published": entry.published
            })
            if len(results) >= max_items:
                break

        print(f"[SCRAPER] ✅ Ditemukan {len(results)} video dari RSS (include_sent={include_sent})")
    except Exception as e:
        print(f"[SCRAPER] ❌ Gagal ambil RSS: {e}")
    return results
