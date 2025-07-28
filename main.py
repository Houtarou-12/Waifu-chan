import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.scraper import (
    RSS_URL,
    YT_CHANNEL_URL,
    get_latest_posts, get_latest_rss_videos,
    load_sent_post_ids, save_sent_post_ids,
    load_sent_video_ids, save_sent_video_ids
)

# 🔧 Load konfigurasi
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
VIDEO_CHANNEL_ID = int(os.getenv("VIDEO_CHANNEL_ID", "0"))

if CHANNEL_ID == 0 or VIDEO_CHANNEL_ID == 0:
    print("[WARN] Channel ID belum dikonfigurasi di .env!")

# 🔌 Setup Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="~", intents=intents)

# 🔁 Loop Komunitas Otomatis
@tasks.loop(seconds=30)
async def check_community():
    print("[LOOP] check_community aktif...")
    sent_post_ids = load_sent_post_ids()
    new_posts = get_latest_posts(YT_CHANNEL_URL, max_posts=5)

    if not new_posts:
        print("[INFO] Tidak ada post valid.")
        return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] Channel komunitas ID ({CHANNEL_ID}) tidak ditemukan!")
        return

    for post in new_posts:
        if post["id"] not in sent_post_ids:
            print(f"[POST] Post baru terdeteksi: {post['id']}")
            embed = discord.Embed(
                title="Post Komunitas Baru",
                url=post["url"],
                description=f"📝 {post['text'] or '(Tanpa teks)'}\n📅 {post['timestamp']}",
                color=discord.Color.blue()
            )
            embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
            embed.set_footer(text="Notifikasi komunitas oleh Waifu-chan❤️")

            await channel.send(embed=embed)
            sent_post_ids.append(post["id"])

    save_sent_post_ids(sent_post_ids)

# 🔁 Loop Video Otomatis (RSS)
@tasks.loop(seconds=30)
async def check_video():
    print("[LOOP] check_video aktif...")
    sent_video_ids = load_sent_video_ids()
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
        published = video.get("published", "Tanggal tidak tersedia")

        print(f"[VIDEO] Periksa: {title} | ID: {video_id}")

        if video_id not in sent_video_ids:
            embed = discord.Embed(
                title=f"{title} | Episode Baru 🎬",
                url=url,
                description=f"📅 Dijadwalkan tayang pada `{published}`",
                color=discord.Color.red()
            )
            embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
            embed.set_image(url=thumbnail_url)
            embed.set_footer(text="Notifikasi video oleh Waifu-chan❤️")

            try:
                await notif_channel.send(embed=embed)
                print(f"[SEND] Embed dikirim ke channel: {notif_channel.name}")
            except Exception as e:
                print(f"[ERROR] Gagal kirim embed: {e}")
            sent_video_ids.append(video_id)

    save_sent_video_ids(sent_video_ids)

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
