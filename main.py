import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import json
from datetime import datetime, timezone, timedelta

from utils.scraper import (
    RSS_URL,
    YT_CHANNEL_URL,
    get_latest_posts, get_latest_rss_videos
)

# 🔧 Load konfigurasi
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
VIDEO_CHANNEL_ID = int(os.getenv("VIDEO_CHANNEL_ID", "0"))

if CHANNEL_ID == 0 or VIDEO_CHANNEL_ID == 0:
    print("[WARN] Channel ID belum dikonfigurasi di .env!")

# ⏰ Zona Waktu Indonesia (WIB)
WIB = timezone(timedelta(hours=7))

# 🔌 Setup Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="~", intents=intents)

# 🔁 Loop Komunitas Otomatis
@tasks.loop(seconds=30)
async def check_community():
    print("[LOOP] check_community aktif...")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            sent_post_ids = data.get("sent_post_ids", {})
    except Exception as e:
        print(f"[ERROR] Gagal load sent_post_ids: {e}")
        sent_post_ids = {}

    # ✨ Konversi array lama ke dictionary
    if isinstance(sent_post_ids, list):
        sent_post_ids = {post_id: "converted" for post_id in sent_post_ids}
        print("[INFO] sent_post_ids lama terdeteksi. Auto-konversi ke dict.")

    new_posts = get_latest_posts(YT_CHANNEL_URL, max_posts=5)
    if not new_posts:
        print("[INFO] Tidak ada post valid.")
        return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] Channel komunitas ID ({CHANNEL_ID}) tidak ditemukan!")
        return

    for post in new_posts:
        post_id = post["id"]
        if post_id not in sent_post_ids:
            print(f"[POST] Post baru terdeteksi: {post_id}")
            embed = discord.Embed(
                title="Post Komunitas Baru",
                url=post["url"],
                description=f"📝 {post['text'] or '(Tanpa teks)'}\n📅 {post['timestamp']}",
                color=discord.Color.blue()
            )
            embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
            embed.set_footer(text="Notifikasi komunitas oleh Waifu-chan❤️")

            try:
                await channel.send(embed=embed)
                sent_post_ids[post_id] = datetime.utcnow().isoformat()
            except Exception as e:
                print(f"[ERROR] Gagal kirim embed komunitas: {e}")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data["sent_post_ids"] = sent_post_ids

    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("[SAVE] sent_post_ids berhasil disimpan.")
    except Exception as e:
        print(f"[ERROR] Gagal simpan data.json: {e}")

# 🔁 Loop Video Otomatis
@tasks.loop(seconds=30)
async def check_video():
    print("[LOOP] check_video aktif...")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            sent_video_ids = data.get("sent_video_ids", {})
    except Exception as e:
        print(f"[ERROR] Gagal load sent_video_ids: {e}")
        sent_video_ids = {}

    # ✨ Konversi array lama ke dictionary
    if isinstance(sent_video_ids, list):
        sent_video_ids = {vid_id: "converted" for vid_id in sent_video_ids}
        print("[INFO] sent_video_ids lama terdeteksi. Auto-konversi ke dict.")

    new_videos = get_latest_rss_videos()
    if not new_videos:
        print("[INFO] Tidak ada video RSS valid.")
        return

    notif_channel = bot.get_channel(VIDEO_CHANNEL_ID)
    if not notif_channel:
        print(f"[ERROR] Channel video ID ({VIDEO_CHANNEL_ID}) tidak ditemukan!")
        return

    for video in new_videos:
        video_id = video["id"]
        title = video["title"]
        url = video["url"]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        published_raw = video.get("published")

        # 🕒 Konversi ke WIB
        try:
            dt_utc = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
            published_wib = dt_utc.astimezone(WIB).strftime("%A, %d %B %Y - %H:%M WIB")
        except Exception as e:
            print(f"[WARN] Gagal parsing waktu tayang: {e}")
            published_wib = "Tanggal tidak tersedia"

        print(f"[VIDEO] Periksa: {title} | ID: {video_id}")
        if video_id not in sent_video_ids:
            embed = discord.Embed(
                title=f"{title} | Episode Baru 🎬",
                url=url,
                description=f"📅 Rilis `{published_wib}`",
                color=discord.Color.red()
            )
            embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
            embed.set_image(url=thumbnail_url)
            embed.set_footer(text="Notifikasi video oleh Waifu-chan❤️")

            try:
                await notif_channel.send(embed=embed)
                sent_video_ids[video_id] = datetime.utcnow().isoformat()
                print(f"[SEND] Embed dikirim ke channel: {notif_channel.name}")
            except Exception as e:
                print(f"[ERROR] Gagal kirim embed video: {e}")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data["sent_video_ids"] = sent_video_ids

    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("[SAVE] sent_video_ids berhasil disimpan.")
    except Exception as e:
        print(f"[ERROR] Gagal simpan data.json: {e}")

# 🔌 Bot Ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🧠 Commands aktif: {[cmd.name for cmd in bot.commands]}")
    check_community.start()
    check_video.start()

    await bot.load_extension("commands.peraturan")
    await bot.load_extension("commands.admin_owner")
    await bot.load_extension("commands.botinfo")

# 🚀 Jalankan Bot
bot.run(TOKEN)