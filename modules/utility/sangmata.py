"""
Module: sangmata
Commands: .sangmata, .names, .usernames
Fetch name/username history via @SangMata bot.
"""

import asyncio
from pyrogram.types import Message
from pyrogram.errors import YouBlockedUser

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel, get_name

MODULE = "sangmata"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}sangmata` — Cek riwayat nama/username user (via @SangMata_BOT)
• `{CMD_HANDLER}names` — Riwayat nama saja
• `{CMD_HANDLER}usernames` — Riwayat username saja
"""
eleger.CMD_HELP[MODULE] = HELP

_SANGMATA_BOT = "SangMata_BOT"


async def _query_sangmata(client, user_id: int, query: str) -> str:
    """Send a query to SangMata bot and return its reply."""
    try:
        response = await client.ask(
            _SANGMATA_BOT,
            query,
            timeout=15,
        )
        return response.text or "_(tidak ada balasan)_"
    except YouBlockedUser:
        return "❌ Kamu memblokir @SangMata_BOT. Buka blokir terlebih dahulu."
    except asyncio.TimeoutError:
        return "❌ @SangMata_BOT tidak merespons (timeout)."
    except Exception as e:
        return f"❌ Error: `{e}`"


@eleger_cmd(r"sangmata$")
async def sangmata_cmd(client, message: Message):
    """Get full name+username history from SangMata."""
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await edel(message, "⚠️ Reply ke pesan user yang ingin dicek.", 5)

    target = reply.from_user
    uid = target.id
    await message.edit(f"`🔍 Mengambil riwayat dari SangMata untuk ID {uid}...`")

    result = await _query_sangmata(client, uid, f"/search {uid}")
    await message.edit(
        f"📋 **SangMata — Riwayat `{get_name(target)}`**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{result[:3500]}"
    )


@eleger_cmd(r"names$")
async def names_cmd(client, message: Message):
    """Get name history from SangMata."""
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await edel(message, "⚠️ Reply ke pesan user.", 5)

    uid = reply.from_user.id
    await message.edit("`🔍 Mengambil riwayat nama...`")
    result = await _query_sangmata(client, uid, f"/names {uid}")
    await message.edit(
        f"📋 **Riwayat Nama — ID `{uid}`**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{result[:3500]}"
    )


@eleger_cmd(r"usernames$")
async def usernames_cmd(client, message: Message):
    """Get username history from SangMata."""
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await edel(message, "⚠️ Reply ke pesan user.", 5)

    uid = reply.from_user.id
    await message.edit("`🔍 Mengambil riwayat username...`")
    result = await _query_sangmata(client, uid, f"/usernames {uid}")
    await message.edit(
        f"📋 **Riwayat Username — ID `{uid}`**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{result[:3500]}"
    )
