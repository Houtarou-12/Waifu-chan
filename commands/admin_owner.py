
from discord.ext import commands
import discord
import os

clear_buffer = {}

def setup_admin_owner_commands(bot, COMMUNITY_CHANNEL_ID, VIDEO_CHANNEL_ID, YT_CHANNEL_URL, sent_post_ids):

    @bot.command()
    async def cekpost_all(ctx):
        posts = get_latest_posts(YT_CHANNEL_URL, max_posts=3)
        if not posts:
            await ctx.send("❌ Tidak bisa ambil post komunitas.")
            return
        for post in posts:
            content = f"📌 Post komunitas:\n{post['url']}"
            if post.get("text"):
                content += f"\n\n📝 {post['text']}\n🕒 {post['timestamp']}"
            await ctx.send(content)

    @bot.command()
    async def to(ctx, channel_id: int = None, *, pesan: str = None):
        if not channel_id or not pesan:
            await ctx.send("❌ Format: `!~to <channel_id> <pesan>`")
            return
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(pesan)
            await ctx.send(f"✅ Pesan dikirim ke `{channel.name}`.")
        else:
            await ctx.send("❌ Channel tidak ditemukan.")

    @bot.command()
    async def tendangpengguna(ctx, member: discord.Member = None, *, alasan: str = "Melanggar peraturan"):
        if ctx.author.guild_permissions.kick_members:
            if not member:
                await ctx.send("❌ Kamu harus menyebut user yang akan dikick.")
                return
            try:
                await member.kick(reason=alasan)
                await ctx.send(f"👢 `{member.display_name}` telah dikick. Alasan: {alasan}")
            except Exception as e:
                await ctx.send(f"❌ Gagal kick: {e}")
        else:
            await ctx.send("❌ Kamu tidak punya izin untuk kick member.")

    @bot.command()
    async def clear(ctx, jumlah: str = None, user: discord.Member = None, *, keyword: str = None):
        if jumlah == "all":
            jumlah = 100
        try:
            jumlah = int(jumlah)
        except:
            jumlah = 10
        if jumlah < 1 or jumlah > 100:
            await ctx.send("❌ Jumlah harus antara 1–100.")
            return

        clear_buffer[ctx.author.id] = {
            "jumlah": jumlah,
            "user": user.id if user else None,
            "keyword": keyword
        }

        message = f"⚠️ Kamu akan menghapus {jumlah} pesan"
        if user:
            message += f" dari `{user.display_name}`"
        if keyword:
            message += f" yang mengandung kata: `{keyword}`"
        message += "\nKetik `!~confirmclear` untuk melanjutkan."
        await ctx.send(message)

    @bot.command()
    async def confirmclear(ctx):
        args = clear_buffer.get(ctx.author.id)
        if not args:
            await ctx.send("❌ Tidak ada permintaan penghapusan yang tertunda.")
            return

        def check(m):
            if args["user"] and m.author.id != args["user"]:
                return False
            if args["keyword"] and args["keyword"].lower() not in m.content.lower():
                return False
            return True

        deleted = await ctx.channel.purge(limit=args["jumlah"], check=check)
        await ctx.send(f"🧹 `{ctx.author.display_name}` menghapus {len(deleted)} pesan.", delete_after=5)
        clear_buffer.pop(ctx.author.id, None)