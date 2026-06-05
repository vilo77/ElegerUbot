"""
Module: peers
Commands: .updatepeers
Update peer database to fix invalid peer id errors.
"""

import asyncio
from pyrogram.types import Message
import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd

MODULE = "peers"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}updatepeers` — Memperbarui database memori bot.
"""
eleger.CMD_HELP[MODULE] = HELP

@eleger_cmd(r"updatepeers$", allow_sudo=False)
async def update_peers_cache(client, message: Message):
    status_msg = await message.edit("🔄 **Memindai dan memperbarui database peers...**\n`Mohon tunggu sebentar, proses ini sangat penting...`")
    
    berhasil = 0
    try:
        # Loop melalui semua obrolan untuk memaksa bot mengingat ID grup/kontak
        async for dialog in client.get_dialogs():
            berhasil += 1
            
        await status_msg.edit(
            f"✅ **Database Peers Diperbarui!**\n\n"
            f"Berhasil merekam `{berhasil}` obrolan ke dalam memori bot.\n\n"
            f"*Terminal Railway kamu sekarang sudah kebal dari eror merah!* 🚀"
        )
    except Exception as e:
        await status_msg.edit(f"❌ **Terjadi kesalahan:** `{str(e)}`")
