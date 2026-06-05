"""
Module: broadcast
Commands: .gcast, .gcast -group, .gcast -channel
Broadcast a message to all dialogs.
"""

import asyncio
from pyrogram.types import Message
from pyrogram.enums import ChatType

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "broadcast"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}gcast` — Broadcast ke semua grup & channel
• `{CMD_HANDLER}gcast -group` — Broadcast ke grup saja
• `{CMD_HANDLER}gcast -channel` — Broadcast ke channel saja
• `{CMD_HANDLER}gcast -user` — Broadcast ke semua private chat

⚠️ Gunakan dengan hati-hati! Risiko flood wait.
"""
eleger.CMD_HELP[MODULE] = HELP

_RUNNING: dict[int, bool] = {}  # {client_index: is_running}


@eleger_cmd(r"gcast(?: (-.+))?$", allow_sudo=False)
async def gcast_cmd(client, message: Message):
    """Broadcast replied message to all dialogs."""
    cid = client.client_index

    if _RUNNING.get(cid):
        return await message.edit("⚠️ Broadcast masih berjalan. Ketik `.stopcast` untuk berhenti.")

    reply = message.reply_to_message
    if not reply:
        return await edel(message, "⚠️ Reply ke pesan yang ingin di-broadcast.", 5)

    flag = (message.matches[0].group(1) or "").strip().lower()
    target_types: list[ChatType] = []
    if flag == "-group":
        target_types = [ChatType.GROUP, ChatType.SUPERGROUP]
    elif flag == "-channel":
        target_types = [ChatType.CHANNEL]
    elif flag == "-user":
        target_types = [ChatType.PRIVATE]
    else:
        target_types = [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]

    status_msg = await message.edit("`📡 Memulai broadcast...`")
    _RUNNING[cid] = True

    sent = 0
    failed = 0
    skipped = 0

    try:
        async for dialog in client.get_dialogs():
            if not _RUNNING.get(cid):
                break
            chat = dialog.chat
            if chat.type not in target_types:
                skipped += 1
                continue
            try:
                # KUNCI PERUBAHAN: Menggunakan fungsi copy() agar tidak ada tag forward
                await reply.copy(chat.id)
                sent += 1
                await asyncio.sleep(1.5)
            except Exception:
                failed += 1
                await asyncio.sleep(0.5)

            # Update status every 10 sends
            if (sent + failed) % 10 == 0:
                try:
                    await status_msg.edit(
                        f"📡 **Broadcasting...**\n"
                        f"✅ Terkirim: `{sent}`\n"
                        f"❌ Gagal: `{failed}`\n"
                        f"⏭ Skip: `{skipped}`"
                    )
                except Exception:
                    pass
    finally:
        _RUNNING[cid] = False

    await status_msg.edit(
        f"📡 **Broadcast Selesai!**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ **Terkirim:** `{sent}`\n"
        f"❌ **Gagal:** `{failed}`\n"
        f"⏭ **Skip:** `{skipped}`"
    )


@eleger_cmd(r"stopcast$", allow_sudo=False)
async def stopcast_cmd(client, message: Message):
    """Stop ongoing broadcast."""
    cid = client.client_index
    if _RUNNING.get(cid):
        _RUNNING[cid] = False
        await message.edit("⛔ **Broadcast dihentikan.**")
    else:
        await message.edit("✅ Tidak ada broadcast yang berjalan.")
