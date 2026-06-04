"""
Module: whois
Commands: .whois [username|id|reply]
"""

import aiohttp
from pyrogram.types import Message
from pyrogram.errors import UsernameNotOccupied, PeerIdInvalid

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import get_name, edel

MODULE = "whois"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}whois` — Lookup user dari reply, username, atau ID
• `{CMD_HANDLER}whois @username` — Lookup user berdasarkan username
• `{CMD_HANDLER}whois <id>` — Lookup user berdasarkan ID
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"whois(?: (.+))?$")
async def whois_cmd(client, message: Message):
    """Detailed user lookup."""
    arg = message.matches[0].group(1)
    await message.edit("`🔍 Mencari info user...`")

    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            uid = message.reply_to_message.from_user.id
        elif arg:
            target = arg.strip().lstrip("@")
            try:
                uid = int(target)
            except ValueError:
                uid = target
        else:
            uid = "me"
            
        user = await client.get_users(uid)
        try:
            full_chat = await client.get_chat(user.id)
        except Exception:
            full_chat = None
            
    except (UsernameNotOccupied, PeerIdInvalid, KeyError):
        return await message.edit("❌ User tidak ditemukan.")
    except Exception as e:
        return await message.edit(f"❌ Error: `{e}`")

    if not user:
        return await message.edit("❌ User tidak ditemukan.")

    name = get_name(user)
    username = f"@{user.username}" if user.username else "–"
    uid = user.id
    dc = getattr(user, "dc_id", "–")
    bio = getattr(full_chat, "bio", None) if full_chat else "–"
    if not bio:
        bio = "–"
    phone = getattr(user, "phone_number", None) or "–"
    is_bot = "🤖 Ya" if user.is_bot else "👤 Tidak"
    is_premium = "⭐ Ya" if getattr(user, "is_premium", False) else "Tidak"
    is_verified = "✅ Ya" if user.is_verified else "Tidak"
    is_restricted = "⚠️ Ya" if user.is_restricted else "Tidak"
    is_scam = "🚨 Ya" if getattr(user, "is_scam", False) else "Tidak"
    is_fake = "🎭 Ya" if getattr(user, "is_fake", False) else "Tidak"
    is_deleted = "🗑 Ya" if user.is_deleted else "Tidak"

    # Mutual chats count (best effort)
    full = full_chat

    text = (
        f"🔍 **Who Is?**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 **Nama:** [{name}](tg://user?id={uid})\n"
        f"🆔 **ID:** `{uid}`\n"
        f"📛 **Username:** {username}\n"
        f"📡 **DC ID:** `{dc}`\n"
        f"📱 **Phone:** `{phone}`\n"
        f"📝 **Bio:** `{bio[:200]}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** {is_bot}\n"
        f"⭐ **Premium:** {is_premium}\n"
        f"✅ **Verified:** {is_verified}\n"
        f"⚠️ **Restricted:** {is_restricted}\n"
        f"🚨 **Scam:** {is_scam}\n"
        f"🎭 **Fake:** {is_fake}\n"
        f"🗑 **Deleted:** {is_deleted}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🔗 [Buka Profil](tg://user?id={uid})"
    )
    await message.edit(text, disable_web_page_preview=True)
