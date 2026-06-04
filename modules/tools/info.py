"""
Module: info
Commands: .info, .chatinfo, .id
"""

from pyrogram.types import Message
from pyrogram.enums import ChatType

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import get_name, mention

MODULE = "info"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}info` — Info user sendiri / reply ke user lain
• `{CMD_HANDLER}chatinfo` — Info grup/channel saat ini
• `{CMD_HANDLER}id` — Tampilkan ID chat & user
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"info$")
async def info_cmd(client, message: Message):
    """Get info about a user."""
    await message.edit("`⏳ Fetching user info...`")
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    else:
        target = message.from_user

    if target is None:
        return await message.edit("❌ Tidak bisa mendapatkan info user.")

    try:
        user = await client.get_chat(target.id)
    except Exception as e:
        return await message.edit(f"❌ Error: `{e}`")

    name = get_name(user)
    username = f"@{user.username}" if user.username else "–"
    bio = getattr(user, "bio", None) or "–"
    dc = getattr(user, "dc_id", "–")
    verified = "✅" if getattr(user, "is_verified", False) else "❌"
    bot = "🤖 Ya" if getattr(user, "is_bot", False) else "👤 Tidak"
    premium = "⭐ Ya" if getattr(user, "is_premium", False) else "Tidak"
    restricted = "⚠️ Ya" if getattr(user, "is_restricted", False) else "Tidak"
    deleted = "🗑 Ya" if getattr(user, "is_deleted", False) else "Tidak"

    text = (
        f"👤 **User Info**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🏷 **Nama:** {mention(user)}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"📛 **Username:** {username}\n"
        f"📡 **DC:** `{dc}`\n"
        f"🤖 **Bot:** {bot}\n"
        f"⭐ **Premium:** {premium}\n"
        f"✅ **Verified:** {verified}\n"
        f"⚠️ **Restricted:** {restricted}\n"
        f"🗑 **Deleted:** {deleted}\n"
        f"📝 **Bio:** `{bio[:200]}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🔗 [Link Profil](tg://user?id={user.id})"
    )
    await message.edit(text, disable_web_page_preview=True)


@eleger_cmd(r"chatinfo$")
async def chatinfo_cmd(client, message: Message):
    """Get info about current chat."""
    await message.edit("`⏳ Fetching chat info...`")
    chat = message.chat
    try:
        full_chat = await client.get_chat(chat.id)
    except Exception as e:
        return await message.edit(f"❌ Error: `{e}`")

    ctype = full_chat.type.name.capitalize()
    username = f"@{full_chat.username}" if full_chat.username else "–"
    members = getattr(full_chat, "members_count", "–")
    desc = getattr(full_chat, "description", None) or "–"
    dc = getattr(full_chat, "dc_id", "–")
    restricted = "⚠️ Ya" if getattr(full_chat, "is_restricted", False) else "Tidak"
    verified = "✅" if getattr(full_chat, "is_verified", False) else "❌"
    scam = "🚨 Ya" if getattr(full_chat, "is_scam", False) else "Tidak"

    text = (
        f"💬 **Chat Info**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🏷 **Nama:** `{full_chat.title or get_name(full_chat)}`\n"
        f"🆔 **ID:** `{full_chat.id}`\n"
        f"📛 **Username:** {username}\n"
        f"📋 **Type:** `{ctype}`\n"
        f"👥 **Members:** `{members}`\n"
        f"📡 **DC:** `{dc}`\n"
        f"✅ **Verified:** {verified}\n"
        f"⚠️ **Restricted:** {restricted}\n"
        f"🚨 **Scam:** {scam}\n"
        f"📝 **Desc:** `{desc[:150]}`"
    )
    await message.edit(text, disable_web_page_preview=True)


@eleger_cmd(r"id$")
async def id_cmd(client, message: Message):
    """Show chat and user ID."""
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "–"
    reply_id = message.reply_to_message.from_user.id if (
        message.reply_to_message and message.reply_to_message.from_user
    ) else None

    text = f"🆔 **Chat ID:** `{chat_id}`\n🆔 **Your ID:** `{user_id}`"
    if reply_id:
        text += f"\n🆔 **Replied User ID:** `{reply_id}`"
    await message.edit(text)
