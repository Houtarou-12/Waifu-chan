import discord
from discord import ui, ButtonStyle, Interaction, Embed
from discord.ext import commands
from utils.scraper import get_latest_posts, get_latest_rss_videos

YT_CHANNEL_URL = "https://www.youtube.com/@MuseIndonesia"
clear_buffer = {}

# 🎯 ─── Tombol Konfirmasi Hapus ───
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
    async def cekpost_all(self, ctx):
        posts = get_latest_posts(YT_CHANNEL_URL, max_posts=3)
        if not posts:
            await ctx.send("❌ Tidak bisa ambil post komunitas.")
            return
        for post in posts:
            content = f"📌 Post komunitas:\n{post['url']}"
            if post.get("text"):
                content += f"\n\n📝 {post['text']}\n🕒 {post['timestamp']}"
            await ctx.send(content)

    @commands.command()
    async def to(self, ctx, channel_id: int = None, *, pesan: str = None):
        if not channel_id or not pesan:
            await ctx.send("❌ Format: `~to <channel_id> <pesan>`")
            return
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(pesan)
            await ctx.send(f"✅ Pesan dikirim ke `{channel.name}`.")
        else:
            await ctx.send("❌ Channel tidak ditemukan.")

    @commands.command()
    async def tendangpengguna(self, ctx, member: discord.Member = None, *, alasan: str = "Melanggar peraturan"):
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("❌ Kamu tidak punya izin untuk kick member.")
            return
        if not member:
            await ctx.send("❌ Kamu harus menyebut user yang akan dikick.")
            return
        try:
            await member.kick(reason=alasan)
            await ctx.send(f"👢 `{member.display_name}` telah dikick. Alasan: {alasan}")
        except Exception as e:
            await ctx.send(f"❌ Gagal kick: {e}")

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
    async def cekpost(self, ctx, jumlah: int = 3):
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
    async def cekvideo(self, ctx, jumlah: int = 3):
        videos = get_latest_rss_videos(YT_CHANNEL_URL, max_posts=jumlah)
        if not videos:
            await ctx.send("❌ Tidak bisa ambil video terbaru.")
            return

        for vid in videos:
            embed = Embed(
                title=f"📹 {vid['title']}",
                url=vid['url'],
                description=vid.get("description", "Tidak ada deskripsi."),
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"🕒 {vid['timestamp']}")
            if vid.get("thumbnail"):
                embed.set_image(url=vid["thumbnail"])
            await ctx.send(embed=embed)

# 📦 ─── Register Cog ───
async def setup(bot):
    await bot.add_cog(AdminOwnerCommands(bot))
