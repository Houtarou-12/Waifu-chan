import os
import json
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from commands.peraturan import setup_peraturan_commands
from commands.admin_owner import setup_admin_owner_commands
from commands.botinfo import setup_botinfo_commands
from utils.scraper import (
    get_latest_posts,
    get_latest_rss_videos,
    load_sent_post_ids, save_sent_post_ids,
    load_sent_video_ids, save_sent_video_ids
)

# 🔧 Load konfigurasi
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
VIDEO_CHANNEL_ID = int(os.getenv("VIDEO_CHANNEL_ID", "0"))
YT_CHANNEL_URL = os.getenv("YT_COMMUNITY_URL", "https://www.youtube.com/@MuseIndonesia")

if CHANNEL_ID == 0 or VIDEO_CHANNEL_ID == 0:
    print("[WARN] Channel ID belum dikonfigurasi di .env!")

# 🔌 Setup Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="w/", intents=intents)

# 🔧 Setup Commands
setup_peraturan_commands(bot)
setup_admin_owner_commands(bot, CHANNEL_ID, CHANNEL_ID, YT_CHANNEL_URL, [])
setup_botinfo_commands(bot)

# 🔁 Loop Komunitas Otomatis
@tasks.loop(seconds=60)
async def check_community():
    sent_post_ids = load_sent_post_ids()
    new_posts = get_latest_posts(YT_CHANNEL_URL, max_posts=5)

    if not new_posts:
        print("[INFO] Tidak ada post valid.")
        return

    channel = bot.get_channel(CHANNEL_ID)
    for post in new_posts:
        if post["id"] not in sent_post_ids:
            embed = discord.Embed(
                title="Post Komunitas Baru",
                url=post["url"],
                description=f"📝 {post['text'] or '(Tanpa teks)'}\n📅 {post['timestamp']}",
                color=discord.Color.blue()
            )
            embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
            embed.set_footer(text="Notifikasi komunitas oleh Waifu-chan❤️")

            if channel:
                await channel.send(embed=embed)
            sent_post_ids.append(post["id"])

    save_sent_post_ids(sent_post_ids)

# 🔁 Loop Video Otomatis (RSS)
@tasks.loop(seconds=60)
async def check_video():
    sent_video_ids = load_sent_video_ids()
    new_videos = get_latest_rss_videos()

    if not new_videos:
        print("[INFO] Tidak ada video RSS valid.")
        return

    channel = bot.get_channel(VIDEO_CHANNEL_ID)
    for video in new_videos:
        if video["id"] not in sent_video_ids:
            embed = discord.Embed(
                title=video["title"],
                url=video["url"],
                description=f"📅 {video['published']}",
                color=discord.Color.red()
            )
            embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
            embed.set_image(url=f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg")
            embed.set_footer(text="Notifikasi video oleh Waifu-chan❤️")

            if channel:
                await channel.send(embed=embed)
            sent_video_ids.append(video["id"])

    save_sent_video_ids(sent_video_ids)

# 🔧 Command Manual Cek Post
@bot.command()
async def cekpost(ctx):
    try:
        await ctx.send("🔍 Mengecek post komunitas terbaru...")

        posts = get_latest_posts(YT_CHANNEL_URL, max_posts=1)
        post = posts[0] if posts else None

        if not post:
            await ctx.send("❌ Tidak ditemukan post komunitas yang valid.")
            return

        embed = discord.Embed(
            title="Post Komunitas Baru",
            url=post["url"],
            description=f"📝 {post['text'] or '(Tanpa teks)'}\n📅 {post['timestamp']}",
            color=discord.Color.blue()
        )
        embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
        embed.set_footer(text="Notifikasi komunitas oleh Waifu-chan❤️")

        await ctx.send(embed=embed)

        sent_post_ids = load_sent_post_ids()
        if post["id"] not in sent_post_ids:
            sent_post_ids.append(post["id"])
            save_sent_post_ids(sent_post_ids)

            notif_channel = bot.get_channel(CHANNEL_ID)
            if notif_channel and notif_channel != ctx.channel:
                await notif_channel.send(embed=embed)

    except Exception as e:
        print(f"[ERROR] Gagal jalankan !~cekpost: {e}")
        await ctx.send(f"❌ Terjadi error saat cek post: {e}")

# 🔧 Command Manual Cek Video RSS
@bot.command(name="cekvideo")
async def cekvideo(ctx):
    try:
        await ctx.send("📺 Mengecek video terbaru dari RSS...")

        videos = get_latest_rss_videos()
        video = videos[0] if videos else None

        if not video:
            await ctx.send("❌ Tidak ditemukan video terbaru.")
            return

        embed = discord.Embed(
            title=video["title"],
            url=video["url"],
            description=f"📅 {video['published']}",
            color=discord.Color.red()
        )
        embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
        embed.set_image(url=f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg")
        embed.set_footer(text="Notifikasi video oleh Waifu-chan❤️")

        await ctx.send(embed=embed)

        # 🔔 Deteksi dan kirim ke channel video utama jika belum pernah dikirim
        sent_ids = load_sent_video_ids()
        if video["id"] not in sent_ids:
            sent_ids.append(video["id"])
            save_sent_video_ids(sent_ids)

            notif_channel = bot.get_channel(VIDEO_CHANNEL_ID)
            if notif_channel and notif_channel != ctx.channel:
                await notif_channel.send(embed=embed)

    except Exception as e:
        print(f"[ERROR] Gagal jalankan !~cekvideo: {e}")
        await ctx.send(f"❌ Terjadi error saat cek video: {e}")

# 🔌 Bot Siap Jalan
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🧠 Commands aktif: {[cmd.name for cmd in bot.commands]}")
    check_community.start()
    check_video.start()

# 🚀 Jalankan Bot
bot.run(TOKEN)