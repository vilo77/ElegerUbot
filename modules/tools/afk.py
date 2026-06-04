"""
Module: afk
Commands: .afk [reason], .unafk
"""

import asyncio
import time
from pyrogram import filters
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import get_name, uptime_str

MODULE = "afk"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}afk [alasan]` — Aktifkan mode AFK
• `{CMD_HANDLER}unafk` — Nonaktifkan mode AFK
"""
eleger.CMD_HELP[MODULE] = HELP

# AFK state per client_id
_AFK: dict[int, dict] = {}  # {client_id: {"since": float, "reason": str}}


@eleger_cmd(r"afk(?: (.+))?$")
async def afk_cmd(client, message: Message):
    cid = client.client_index
    reason = message.matches[0].group(1) or "Tidak ada alasan"
    _AFK[cid] = {"since": time.time(), "reason": reason}
    await message.edit(f"😴 **AFK Mode Aktif**\n📝 Alasan: `{reason}`")


@eleger_cmd(r"unafk$")
async def unafk_cmd(client, message: Message):
    cid = client.client_index
    if cid not in _AFK:
        return await message.edit("✅ Kamu tidak sedang AFK.")
    data = _AFK.pop(cid)
    duration = uptime_str(data["since"])
    await message.edit(f"✅ **AFK Mode Nonaktif**\n⏱ Durasi: `{duration}`")


# AFK auto-reply handler (incoming mentions)
from pyrogram.handlers import MessageHandler
from eleger.helpers.decorator import _PENDING_HANDLERS


async def _afk_watcher(client, message: Message):
    cid = client.client_index
    if cid not in _AFK:
        return
    me = client._me
    # Only trigger on mentions or PM
    text = message.text or ""
    if message.mentioned or (message.chat.type.name == "PRIVATE"):
        data = _AFK[cid]
        duration = uptime_str(data["since"])
        name = get_name(me)
        try:
            await message.reply(
                f"😴 **{name}** sedang AFK\n"
                f"📝 Alasan: `{data['reason']}`\n"
                f"⏱ Sejak: `{duration}` lalu"
            )
        except Exception:
            pass


def _register_afk(c):
    c.add_handler(
        MessageHandler(_afk_watcher, filters.incoming & ~filters.me),
        group=10,
    )


_PENDING_HANDLERS.append(_register_afk)
