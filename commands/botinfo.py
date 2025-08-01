from discord.ext import commands
import discord

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
                "`~cekpost_all` — Tampilkan semua post komunitas"
            ),
            inline=False
        )

        embed.add_field(
            name="🔒 Admin & Owner Only",
            value=(
                "`~clear` — Hapus pesan sesuai filter\n"
                "`~confirmclear` — Konfirmasi penghapusan\n"
                "`~kickout @user` — Kick member dari server\n"
                "`~vkick @user` — Kick dari voice channel\n"
                "`~forward #channel <pesan>` — Kirim pesan ke channel lain (dengan nama pengirim)\n"
                "`~to <channel_id> <pesan>` — Kirim pesan anonim ke channel terdaftar\n"
                "`~tendangpengguna @user` — Kick alternatif (dengan alasan)\n"
                "`~setchannel` — Atur channel utama\n"
                "`~tambahperaturan` / `~editperaturan` / `~hapusperaturan` — Kelola peraturan"
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
