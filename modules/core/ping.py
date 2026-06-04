"""
Module: ping
Commands: .ping
"""

import time
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd

MODULE = "ping"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}ping` — Cek latensi koneksi ke Telegram
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd("ping$")
async def ping_cmd(client, message: Message):
    """Check latency."""
    start = time.monotonic()
    sent = await message.edit("🏓 Pong!")
    end = time.monotonic()
    ms = round((end - start) * 1000, 2)
    await sent.edit(f"🏓 **Pong!**\n⚡ `{ms} ms`")
