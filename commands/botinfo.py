from discord.ext import commands
import discord

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["helps"])
    async def waifuhelp(self, ctx):
        embed = discord.Embed(
            title="📖 Daftar Perintah Waifu-chan",
            description="Berikut command yang tersedia berdasarkan role kamu.",
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
                "`~cekpost_all` — Tampilkan semua post komunitas"
            ),
            inline=False
        )

        embed.add_field(
            name="🔒 Admin / Owner Only",
            value=(
                "`~clear [...]` — Hapus pesan sesuai filter\n"
                "`~confirmclear` — Konfirmasi penghapusan\n"
                "`~kickout @user` — Kick member dari server\n"
                "`~vkick @user` — Kick dari voice channel\n"
                "`~forward #channel <pesan>` — Kirim pesan dengan identitas pengirim\n"
                "`~to <pesan>` — Kirim pesan anonim ke channel utama\n"
                "`~setchannel` — Atur channel utama untuk `~to`\n"
                "`~tambahperaturan <isi>` — Tambahkan peraturan baru\n"
                "`~editperaturan <no> <isi>` — Edit peraturan yang ada\n"
                "`~hapusperaturan <no>` — Hapus peraturan ke-n\n"
                "`~resetperaturan` — Reset semua peraturan"
            ),
            inline=False
        )

        embed.add_field(
            name="🧪 Tambahan / Fitur Testing",
            value=(
                "`~embed_post` — Generate embed dari post komunitas\n"
                "`~embed_video` — Generate embed dari video terbaru\n"
                "`~tes_notif` — Test notifikasi manual (video/post)"
            ),
            inline=False
        )

        embed.set_footer(text="Versi: Waifu-chan v1.0 • ©2025 Jafar")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("🏓 Pong! Bot aktif dan responsif.")

async def setup(bot):
    await bot.add_cog(BotInfo(bot))
