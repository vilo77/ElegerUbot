import asyncio
from pyrogram import Client, filters
import eleger

# === LABEL IDENTITAS UNTUK MENU .HELP ===
MODULE = "peers"
HELP = f"""
**Plugin:** `{MODULE}`

• `.updatepeers` — Memperbarui database.........
"""
eleger.CMD_HELP[MODULE] = HELP
# ========================================

@Client.on_message(filters.command(["updatepeers"], prefixes=".") & filters.me)
async def update_peers_cache(client, message):
    msg = await message.edit_text("🔄 **Memindai dan memperbarui database peers...**\n`Mohon tunggu sebentar, proses ini sangat penting...`")
    
    berhasil = 0
    try:
        # Loop melalui semua obrolan untuk memaksa bot mengingat ID grup/kontak
        async for dialog in client.get_dialogs():
            berhasil += 1
            
        await msg.edit_text(f"✅ **Database Peers Diperbarui!**\n\nBerhasil merekam `{berhasil}` obrolan ke dalam memori bot.\n\n*Terminal Railway kamu sekarang sudah kebal dari eror merah!* 🚀")
    except Exception as e:
        await msg.edit_text(f"❌ **Terjadi kesalahan:** `{str(e)}`")
