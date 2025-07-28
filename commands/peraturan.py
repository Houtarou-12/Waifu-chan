from discord.ext import commands
import discord
import json
import os

PERATURAN_FILE = "rules.json"
pending_reset = set()

def load_peraturan():
    if not os.path.exists(PERATURAN_FILE):
        return []
    try:
        with open(PERATURAN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_peraturan(data):
    with open(PERATURAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class Peraturan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def peraturan(self, ctx, nomor: int = None):
        data = load_peraturan()
        if not data:
            await ctx.send("📄 Belum ada peraturan yang disimpan.")
            return

        if nomor is None:
            embed = discord.Embed(
                title="📜 Daftar Peraturan Server",
                color=discord.Color.orange()
            )
            full_text = ""
            for i, isi in enumerate(data, start=1):
                full_text += f"{i}. {isi}\n\n"
            embed.description = full_text.strip()
            await ctx.send(embed=embed)
        elif 1 <= nomor <= len(data):
            embed = discord.Embed(
                title=f"📌 Peraturan nomor {nomor}",
                description=f"{nomor}. {data[nomor - 1]}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Nomor peraturan tidak ditemukan.")

    @commands.command()
    async def tambahperaturan(self, ctx, *, isi: str = None):
        if not isi:
            await ctx.send("❌ Kamu harus memberikan isi peraturan.")
            return
        data = load_peraturan()
        data.append(isi)
        save_peraturan(data)
        await ctx.send(f"✅ Peraturan ditambahkan sebagai nomor {len(data)}.")

    @commands.command()
    async def editperaturan(self, ctx, nomor: int = None, *, isi: str = None):
        data = load_peraturan()
        if not nomor or not isi:
            await ctx.send("❌ Format harus `!~editperaturan <no> <isi baru>`.")
            return
        if not (1 <= nomor <= len(data)):
            await ctx.send("❌ Nomor peraturan tidak valid.")
            return
        data[nomor - 1] = isi
        save_peraturan(data)
        await ctx.send(f"✏️ Peraturan nomor {nomor} telah diubah.")

    @commands.command()
    async def hapusperaturan(self, ctx, nomor: int = None):
        data = load_peraturan()
        if not nomor or not (1 <= nomor <= len(data)):
            await ctx.send("❌ Nomor peraturan tidak valid.")
            return
        isi = data.pop(nomor - 1)
        save_peraturan(data)
        await ctx.send(f"🗑️ Peraturan nomor {nomor} telah dihapus:\n`{isi}`")

    @commands.command()
    async def resetperaturan(self, ctx):
        if ctx.author.id in pending_reset:
            if os.path.exists(PERATURAN_FILE):
                os.remove(PERATURAN_FILE)
            pending_reset.remove(ctx.author.id)
            await ctx.send("⚠️ Semua peraturan telah dihapus.")
        else:
            pending_reset.add(ctx.author.id)
            await ctx.send("⚠️ Kamu yakin ingin hapus semua peraturan? Ketik `!~resetperaturan` sekali lagi untuk konfirmasi.")

# 🔧 Setup untuk load sebagai extension
async def setup(bot):
    await bot.add_cog(Peraturan(bot))