import discord
from discord import ui, ButtonStyle, Interaction, Embed
from discord.ext import commands
import os, json, feedparser, requests, re

# 🎯 Target channel
YT_CHANNEL_URL = "https://www.youtube.com/@MuseIndonesia"
RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxnxya_32jcKj4yN1_kD7A"
DATA_FILE = "data.json"
clear_buffer = {}

# 💾 ─── Penyimpanan ID ───
def load_sent_post_ids():
    return _load_json_field("sent_post_ids", warn="data.json belum ada.")

def save_sent_post_ids(post_ids):
    _save_json_field("sent_post_ids", post_ids, "sent_post_ids")

def load_sent_video_ids():
    return _load_json_field("sent_video_ids", warn="data.json belum ada untuk video.")

def save_sent_video_ids(video_ids):
    _save_json_field("sent_video_ids", video_ids, "sent_video_ids")

def _load_json_field(field, warn):
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

# 🔍 ─── Scraper Post Komunitas ───
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

                        thumbnails = post_data.get("backstageAttachment", {}).get("image", {}).get("thumbnails", [])
                        image_url = thumbnails[-1]["url"] if thumbnails else None

                        results.append({
                            "id": post_id,
                            "url": f"https://www.youtube.com/post/{post_id}",
                            "text": text,
                            "timestamp": timestamp,
                            "image": image_url
                        })

                        if len(results) >= max_posts:
                            return results
                    except KeyError:
                        continue
    except Exception as e:
        print(f"[ERROR] Gagal scrape komunitas: {e}")
    return results

# 🔍 ─── Scraper Video via RSS ───
def get_latest_rss_videos(rss_url=RSS_URL, max_posts=3, include_sent=False):
    results = []
    try:
        sent_ids = load_sent_video_ids()
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            video_id = entry.yt_videoid
            if not include_sent and video_id in sent_ids:
                continue

            thumbnail = entry.get("media_thumbnail", [{}])[0].get("url", "")
            description = entry.get("summary", "")

            results.append({
                "id": video_id,
                "title": entry.title,
                "url": entry.link,
                "description": description,
                "thumbnail": thumbnail,
                "timestamp": entry.published
            })

            if len(results) >= max_posts:
                break

        print(f"[SCRAPER] ✅ Ditemukan {len(results)} video dari RSS (include_sent={include_sent})")
    except Exception as e:
        print(f"[SCRAPER] ❌ Gagal ambil RSS: {e}")
    return results

class ConfirmClear(ui.View):
    def __init__(self, key, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.key = key
        self.ctx = ctx

    @ui.button(label="Hapus", style=ButtonStyle.danger)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("🚫 Kamu tidak punya izin!", ephemeral=True)
            return

        try:
            clear_buffer.pop(self.key, None)
            if self.key == "post":
                save_sent_post_ids([])
            elif self.key == "video":
                save_sent_video_ids([])
            await interaction.response.send_message(f"✅ ID {self.key} berhasil dihapus.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Gagal menghapus: {e}", ephemeral=True)

    @ui.button(label="Batal", style=ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message("❎ Dibatalkan.", ephemeral=True)

# ✨ ─── Command untuk Cek Post ───
@bot.command()
async def cekpost(ctx):
    posts = get_latest_posts(YT_CHANNEL_URL, max_posts=3)
    sent_ids = load_sent_post_ids()

    if not posts:
        await ctx.send("📭 Tidak ada post komunitas ditemukan.")
        return

    embeds = []
    for post in posts:
        is_new = post["id"] not in sent_ids
        embed = Embed(title="Post Komunitas", description=post["text"] or "Tanpa teks")
        embed.add_field(name="Waktu", value=post["timestamp"], inline=True)
        embed.add_field(name="Status", value="🆕 Baru!" if is_new else "✅ Sudah dikirim", inline=True)
        if post["image"]:
            embed.set_image(url=post["image"])
        embed.set_footer(text=post["url"])
        embeds.append(embed)

    clear_buffer["post"] = "siap"
    await ctx.send(embeds=embeds, view=ConfirmClear("post", ctx))

# ✨ ─── Command untuk Cek Video ───
@bot.command()
async def cekvideo(ctx):
    videos = get_latest_rss_videos(RSS_URL, max_posts=3)
    sent_ids = load_sent_video_ids()

    if not videos:
        await ctx.send("📼 Tidak ada video terbaru.")
        return

    embeds = []
    for video in videos:
        is_new = video["id"] not in sent_ids
        embed = Embed(title=video["title"], url=video["url"], description=video["description"])
        embed.add_field(name="Waktu", value=video["timestamp"], inline=True)
        embed.add_field(name="Status", value="🆕 Belum dikirim" if is_new else "✅ Sudah dikirim", inline=True)
        embed.set_image(url=video["thumbnail"])
        embeds.append(embed)

    clear_buffer["video"] = "siap"
    await ctx.send(embeds=embeds, view=ConfirmClear("video", ctx))
