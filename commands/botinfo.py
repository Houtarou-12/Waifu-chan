from discord.ext import commands
import discord

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("🏓 Pong! Bot aktif dan responsif.")

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["helps"])
    async def waifuhelp(self, ctx):
        embed = discord.Embed(
            title="📖 Daftar Perintah Waifu-chan",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="💫 Umum",
            value=(
                "`~ping` — Cek apakah bot aktif\n"
                "`~waifuhelp` — Tampilkan daftar perintah\n"
                "`~botinfo` — Info bot dan status sistem\n"
                "`~peraturan` — Lihat semua peraturan server\n"
                "`~peraturan <no>` — Lihat isi peraturan ke-n\n"
                "`~cekvideo` — Tampilkan video terbaru dari channel\n"
                "`~cekpost` — Tampilkan post komunitas terbaru\n"
                "`~cekpost_all` — Tampilkan semua post komunitas (admin bisa pakai)"
            ),
            inline=False
        )

        embed.add_field(
            name="🔒 Admin & Owner Only",
            value=(
                "`~clear [jumlah/@user/kata]` — Hapus pesan sesuai filter (dengan konfirmasi)\n"
                "`~confirmclear` — Tombol konfirmasi untuk penghapusan\n"
                "`~to <channel_id> <pesan>` — Kirim pesan ke channel tertentu\n"
                "`~forward #channel <pesan>` — Kirim embed admin ke channel tertentu\n"
                "`~kickout @user` — Kick member dari server\n"
                "`~vkick @user` — Kick dari voice channel\n"
                "`~setchannel` — Atur channel utama untuk notifikasi otomatis\n"
                "`~tambahperaturan <isi>` — Tambah peraturan baru\n"
                "`~editperaturan <no> <isi>` — Edit peraturan ke-n\n"
                "`~hapusperaturan <no>` — Hapus peraturan ke-n\n"
                "`~resetperaturan` — Hapus semua peraturan dari rules.json"
            ),
            inline=False
        )

        embed.set_footer(text="Versi: Waifu-chan v1.0 • ©2025 Jafar")
        await ctx.send(embed=embed)

# 🔧 Setup untuk extension
async def setup(bot):
    await bot.add_cog(BotInfo(bot))