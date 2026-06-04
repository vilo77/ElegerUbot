"""
Module: purge
Commands: .purge [n], .purgeme [n], .del
"""

import asyncio
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "purge"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}purge` — Hapus semua pesan dari pesan yg direply sampai sekarang
• `{CMD_HANDLER}purge <n>` — Hapus n pesan terakhir
• `{CMD_HANDLER}purgeme <n>` — Hapus n pesan milik saya saja
• `{CMD_HANDLER}del` — Hapus pesan yang direply
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"purge(?: (\d+))?$", group_only=True)
async def purge_cmd(client, message: Message):
    """Purge messages from replied message to now."""
    arg = message.matches[0].group(1)
    chat_id = message.chat.id

    if arg:
        limit = int(arg)
        msg_ids = []
        async for msg in client.get_chat_history(chat_id, limit=limit + 1):
            msg_ids.append(msg.id)
        msg_ids = msg_ids[1:]  # exclude trigger message
    elif message.reply_to_message:
        start_id = message.reply_to_message.id
        end_id = message.id
        msg_ids = list(range(start_id, end_id + 1))
    else:
        return await edel(message, "⚠️ Reply ke pesan atau berikan jumlah.", 5)

    deleted = 0
    # Batch delete in chunks of 100
    chunks = [msg_ids[i:i+100] for i in range(0, len(msg_ids), 100)]
    for chunk in chunks:
        try:
            await client.delete_messages(chat_id, chunk)
            deleted += len(chunk)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except MessageDeleteForbidden:
            pass

    status = await message.reply(f"🗑 **Purged `{deleted}` messages.**")
    await asyncio.sleep(3)
    try:
        await status.delete()
    except Exception:
        pass


@eleger_cmd(r"purgeme(?: (\d+))?$", group_only=True)
async def purgeme_cmd(client, message: Message):
    """Delete my own messages."""
    arg = message.matches[0].group(1)
    limit = int(arg) if arg else 10
    chat_id = message.chat.id
    me = client._me

    msg_ids = []
    async for msg in client.get_chat_history(chat_id, limit=200):
        if msg.from_user and msg.from_user.id == me.id:
            msg_ids.append(msg.id)
            if len(msg_ids) >= limit:
                break

    chunks = [msg_ids[i:i+100] for i in range(0, len(msg_ids), 100)]
    deleted = 0
    for chunk in chunks:
        try:
            await client.delete_messages(chat_id, chunk)
            deleted += len(chunk)
        except Exception:
            pass

    status = await message.reply(f"🗑 **Deleted `{deleted}` of my messages.**")
    await asyncio.sleep(3)
    try:
        await status.delete()
    except Exception:
        pass


@eleger_cmd(r"del$")
async def delete_cmd(client, message: Message):
    """Delete replied message."""
    if message.reply_to_message:
        await message.reply_to_message.delete()
    await message.delete()
