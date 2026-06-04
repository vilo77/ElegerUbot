"""
Module: alive
Commands: .alive
"""

import platform
import sys
import time

from pyrogram import __version__ as pyro_ver
from pyrogram.types import Message

import eleger
from eleger import BOT_NAME, BOT_VERSION, CMD_HANDLER, START_TIME
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import uptime_str

MODULE = "alive"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}alive` — Tampilkan status userbot
• `{CMD_HANDLER}ping` — Cek latensi (ada di modul ping)
"""

eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd("alive$")
async def alive_cmd(client, message: Message):
    """Show userbot status."""
    me = client._me
    total_clients = len(eleger.CLIENTS)
    uptime = uptime_str(START_TIME)

    text = (
        f"⚡ **{BOT_NAME}**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 **User:** [{me.first_name}](tg://user?id={me.id})\n"
        f"🆔 **ID:** `{me.id}`\n"
        f"🤖 **Version:** `{BOT_VERSION}`\n"
        f"📦 **Pyrogram:** `{pyro_ver}`\n"
        f"🐍 **Python:** `{sys.version.split()[0]}`\n"
        f"🖥 **OS:** `{platform.system()} {platform.release()}`\n"
        f"👥 **Clients:** `{total_clients}`\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"📌 **Prefix:** `{CMD_HANDLER}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📚 **Modules:** `{len(eleger.LOADED_MODULES)}`"
    )
    await message.edit(text, disable_web_page_preview=True)
