from discord.ext import commands
import discord

def setup_botinfo_commands(bot):

    @bot.command()
    async def ping(ctx):
        await ctx.send("🏓 Pong! Bot aktif dan responsif.")

    @bot.command(aliases=["helps"])
    async def waifuhelp(ctx):
        embed = discord.Embed(
            title="📖 Daftar Perintah Waifu-chan",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="💫 Umum",
            value=(
                "`!~ping` — Cek apakah bot aktif\n"
                "`!~waifuhelp` — Tampilkan daftar perintah\n"
                "`!~peraturan` — Lihat semua peraturan server\n"
                "`!~peraturan <no>` — Lihat isi peraturan ke-n"
            ),
            inline=True
        )

        embed.add_field(
            name="🔒 Admin Only",
            value=(
                "`!~clear [jumlah/@user/kata]` — Hapus pesan sesuai filter\n"
                "`!~confirmclear` — Konfirmasi pembersihan pesan\n"
                "`!~cekpost` — Kirim ulang post terbaru\n"
                "`!~cekpost all` — Tampilkan 3 post komunitas terbaru\n"
                "`!~cekvideo` — Kirim ulang video terbaru\n"
                "`!~tambahperaturan <isi>` — Tambah peraturan baru\n"
                "`!~editperaturan <no> <isi>` — Edit peraturan ke-n\n"
                "`!~hapusperaturan <no>` — Hapus peraturan ke-n\n"
                "`!~resetperaturan` — Hapus semua peraturan\n"
                "`!~to <channel_id> <pesan>` — Kirim pesan ke channel tertentu\n"
                "`!~tendangpengguna <@user>` — Kick member manual"
            ),
            inline=True
        )

        embed.set_footer(text="Versi: Waifu-chan v1.0 • ©2025 Jafar Studio")
        await ctx.send(embed=embed)