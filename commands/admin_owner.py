import discord
from discord import ui, ButtonStyle, Interaction, Embed
from discord.ext import commands
import os
import json

from utils.scraper import (
    get_latest_posts,
    get_latest_rss_videos,
    load_sent_video_ids,
    save_sent_video_ids,
    YT_CHANNEL_URL
)

VIDEO_CHANNEL_ID = int(os.getenv("VIDEO_CHANNEL_ID", "0"))
FORWARD_CHANNEL_ID = int(os.getenv("FORWARD_CHANNEL_ID", "0"))
clear_buffer = {}

class ConfirmClearView(ui.View):
    def __init__(self, author_id, args):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.args = args

    @ui.button(label="✅ Hapus", style=ButtonStyle.danger)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Ini bukan permintaan kamu.", ephemeral=True)
            return

        jumlah = self.args["jumlah"]
        target_user = self.args["user"]
        keyword = self.args["keyword"]

        def is_target(msg):
            if target_user and msg.author.id != target_user:
                return False
            if keyword and keyword.lower() not in msg.content.lower():
                return False
            return True

        to_delete = []
        async for msg in interaction.channel.history(limit=200):
            if is_target(msg):
                to_delete.append(msg)
            if len(to_delete) >= jumlah:
                break

        try: await self.args["embed_msg"].delete()
        except: pass
        try: await interaction.channel.get_partial_message(self.args["command_msg_id"]).delete()
        except: pass

        if to_delete:
            await interaction.channel.delete_messages(to_delete)

        await interaction.response.send_message(
            f"🧹 `{interaction.user.display_name}` menghapus {len(to_delete)} pesan.",
            delete_after=5
        )

        clear_buffer.pop(self.author_id, None)
        self.stop()

    @ui.button(label="❌ Batal", style=ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Kamu tidak bisa membatalkan permintaan orang lain.", ephemeral=True)
            return

        clear_buffer.pop(self.author_id, None)
        await interaction.response.send_message("🚫 Penghapusan dibatalkan.")
        self.stop()


class AdminOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kickout(self, ctx, member: discord.Member = None, *, alasan: str = "Melanggar aturan"):
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("❌ Kamu tidak punya izin untuk kick member.")
            return
        if not member:
            await ctx.send("❌ Harus menyebut user yang akan dikick.")
            return
        try:
            await member.kick(reason=alasan)
            await ctx.send(f"👢 `{member.display_name}` telah dikick dari server. Alasan: {alasan}")
        except Exception as e:
            await ctx.send(f"❌ Gagal kick: {e}")

    @commands.command()
    async def vkick(self, ctx, member: discord.Member = None):
        if not ctx.author.guild_permissions.move_members:
            await ctx.send("❌ Kamu tidak punya izin untuk mengeluarkan dari VC.")
            return
        if not member or not member.voice:
            await ctx.send("❌ User tidak berada di voice channel.")
            return
        try:
            await member.move_to(None)
            await ctx.send(f"🔊 `{member.display_name}` telah dikeluarkan dari voice channel.")
        except Exception as e:
            await ctx.send(f"❌ Gagal vkick: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def forward(self, ctx, channel: discord.TextChannel = None, *, pesan: str = None):
        if not channel or not pesan:
            await ctx.send("❌ Format: `~forward #channel <pesan>`")
            return
        if not isinstance(channel, discord.TextChannel):
            await ctx.send("🚫 Harus menyebut channel teks yang valid.")
            return

        embed = Embed(description=pesan, color=discord.Color.gold())
        embed.set_footer(text=f"Oleh {ctx.author.display_name}")
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Bot tidak punya izin kirim pesan ke channel tersebut.")

    @commands.command()
    async def to(self, ctx, *, pesan: str = None):
        if not pesan:
            await ctx.send("❌ Format: `~to <pesan>`")
            return
        try:
            channel_id = FORWARD_CHANNEL_ID
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await ctx.send("❌ Channel tujuan tidak ditemukan.")
                return

            embed = Embed(description=pesan, color=discord.Color.blue())
            embed.set_footer(text="🕵️ Pesan anonim")
            await channel.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Bot tidak punya izin untuk kirim ke channel tujuan.")

    @commands.command()
    async def clear(self, ctx, jumlah: str = None, user: discord.Member = None, *, keyword: str = None):
        if jumlah == "all": jumlah = 100
        try: jumlah = int(jumlah)
        except: jumlah = 10
        if jumlah < 1 or jumlah > 100:
            await ctx.send("❌ Jumlah harus antara 1–100.")
            return

        args = {
            "jumlah": jumlah,
            "user": user.id if user else None,
            "keyword": keyword,
            "command_msg_id": ctx.message.id
        }

        desc = f"⚠️ Kamu akan menghapus {jumlah} pesan"
        if user: desc += f" dari `{user.display_name}`"
        if keyword: desc += f" yang mengandung kata: `{keyword}`"
        desc += "\nKlik tombol di bawah untuk konfirmasi atau batal."

        embed = Embed(title="Konfirmasi Penghapusan", description=desc, color=discord.Color.orange())
        embed_msg = await ctx.send(embed=embed)

        args["embed_msg"] = embed_msg
        clear_buffer[ctx.author.id] = args
        await embed_msg.edit(view=ConfirmClearView(ctx.author.id, args))

    @commands.command()
    async def cekpost(self, ctx, jumlah: int = 1):
        posts = get_latest_posts(YT_CHANNEL_URL, max_posts=jumlah)
        if not posts:
            await ctx.send("❌ Tidak bisa ambil post komunitas.")
            return

        for post in posts:
            embed = Embed(
                title="📌 Post Komunitas",
                url=post['url'],
                description=post.get("text", "Tidak ada teks."),
                color=discord.Color.green()
            )
            embed.set_footer(text=f"🕒 {post['timestamp']}")
            if post.get("image"):
                embed.set_image(url=post["image"])
            await ctx.send(embed=embed)

    @commands.command()
    async def cekvideo(self, ctx, jumlah: int = 1):
        videos = get_latest_rss_videos(max_posts=jumlah, include_sent=True)
        sent_ids = load_sent_video_ids()

        try:
            with open("data.json", "r") as f:
                config = json.load(f)
            main_channel_id = config.get("main_channel_id")
            main_channel = self.bot.get_channel(main_channel_id) if main_channel_id else None
        except Exception as e:
            print(f"[ERROR] Gagal ambil channel utama: {e}")
            main_channel = None

        new_ids = []
        for vid in videos:
            is_new = vid["id"] not in sent_ids
            tag = "🆕" if is_new else "✅"
            embed = Embed(
                title=f"{tag} {vid['title']}",
                url=vid["url"],
                description=vid.get("description", "Tidak ada deskripsi."),
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"🕒 {vid['timestamp']}")
            if vid.get("thumbnail"):
                embed.set_image(url=vid["thumbnail"])
            await ctx.send(embed=embed)

            if is_new and main_channel and main_channel != ctx.channel:
                try:
                    await main_channel.send(embed=embed)
                    print(f"[INFO] Video dikirim ke channel utama: {main_channel.name}")
                except Exception as e:
                    print(f"[ERROR] Gagal kirim ke channel utama: {e}")
            if is_new:
                new_ids.append(vid["id"])

        if new_ids:
            save_sent_video_ids(sent_ids + new_ids)

    @commands.command(name="tes_notif")
    @commands.is_owner()
    async def tes_notif(self, ctx):
        videos = get_latest_rss_videos(include_sent=True)
        if not videos:
            await ctx.send("📭 Tidak ada video untuk diuji.")
            return

        channel = self.bot.get_channel(VIDEO_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Channel VIDEO_CHANNEL_ID tidak ditemukan.")
            return

        video = videos[0]
        thumbnail_url = f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg"

        embed = Embed(
            title=f"{video['title']} | Uji Notif 🎬",
            url=video["url"],
            description=f"📅 Dijadwalkan tayang pada `{video.get('published', 'Tanggal tidak tersedia')}`",
            color=discord.Color.red()
        )
        embed.set_author(name="Muse Indonesia", url=YT_CHANNEL_URL)
        embed.set_image(url=thumbnail_url)
        embed.set_footer(text="Notifikasi video oleh Waifu-chan❤️ (Tes Manual)")

        await channel.send(embed=embed)
        await ctx.send(f"✅ Embed video berhasil dikirim ke <#{VIDEO_CHANNEL_ID}>")

async def setup(bot):
    await bot.add_cog(AdminOwnerCommands(bot))