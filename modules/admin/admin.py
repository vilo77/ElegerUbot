"""
Module: admin
Commands: .ban, .unban, .kick, .kickme, .mute, .unmute, .promote, .demote
"""

from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.enums import ChatMemberStatus

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import get_name, edel

MODULE = "admin"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}ban` — Ban user (reply)
• `{CMD_HANDLER}unban` — Unban user (reply)
• `{CMD_HANDLER}kick` — Kick user (reply)
• `{CMD_HANDLER}kickme` — Keluar dari grup
• `{CMD_HANDLER}mute` — Mute user (reply)
• `{CMD_HANDLER}unmute` — Unmute user (reply)
• `{CMD_HANDLER}promote` — Promosikan user jadi admin (reply)
• `{CMD_HANDLER}demote` — Turunkan admin (reply)
"""
eleger.CMD_HELP[MODULE] = HELP


async def _get_target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None


@eleger_cmd(r"ban$", group_only=True, admin_only=True)
async def ban_cmd(client, message: Message):
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin di-ban.", 5)
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.edit(f"🚫 [{get_name(target)}](tg://user?id={target.id}) telah di-**ban**.")
    except ChatAdminRequired:
        await message.edit("❌ Saya bukan admin atau tidak punya hak ban.")


@eleger_cmd(r"unban$", group_only=True, admin_only=True)
async def unban_cmd(client, message: Message):
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin di-unban.", 5)
    try:
        await client.unban_chat_member(message.chat.id, target.id)
        await message.edit(f"✅ [{get_name(target)}](tg://user?id={target.id}) di-**unban**.")
    except ChatAdminRequired:
        await message.edit("❌ Tidak ada hak unban.")


@eleger_cmd(r"kick$", group_only=True, admin_only=True)
async def kick_cmd(client, message: Message):
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin di-kick.", 5)
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        await message.edit(f"👢 [{get_name(target)}](tg://user?id={target.id}) di-**kick**.")
    except ChatAdminRequired:
        await message.edit("❌ Tidak ada hak kick.")


@eleger_cmd(r"kickme$", group_only=True)
async def kickme_cmd(client, message: Message):
    me = client._me
    await message.edit("👋 Keluar dari grup...")
    try:
        await client.leave_chat(message.chat.id)
    except Exception as e:
        await message.edit(f"❌ Gagal keluar: `{e}`")


@eleger_cmd(r"mute$", group_only=True, admin_only=True)
async def mute_cmd(client, message: Message):
    from pyrogram.types import ChatPermissions
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin di-mute.", 5)
    try:
        await client.restrict_chat_member(
            message.chat.id, target.id,
            ChatPermissions(can_send_messages=False)
        )
        await message.edit(f"🔇 [{get_name(target)}](tg://user?id={target.id}) di-**mute**.")
    except ChatAdminRequired:
        await message.edit("❌ Tidak ada hak restrict.")


@eleger_cmd(r"unmute$", group_only=True, admin_only=True)
async def unmute_cmd(client, message: Message):
    from pyrogram.types import ChatPermissions
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin di-unmute.", 5)
    try:
        await client.restrict_chat_member(
            message.chat.id, target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await message.edit(f"🔊 [{get_name(target)}](tg://user?id={target.id}) di-**unmute**.")
    except ChatAdminRequired:
        await message.edit("❌ Tidak ada hak unrestrict.")


@eleger_cmd(r"promote$", group_only=True, admin_only=True)
async def promote_cmd(client, message: Message):
    from pyrogram.types import ChatPrivileges
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin dipromote.", 5)
    try:
        await client.promote_chat_member(
            message.chat.id, target.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
            )
        )
        await message.edit(f"⭐ [{get_name(target)}](tg://user?id={target.id}) di-**promote**.")
    except (ChatAdminRequired, UserAdminInvalid):
        await message.edit("❌ Tidak bisa promote user ini.")


@eleger_cmd(r"demote$", group_only=True, admin_only=True)
async def demote_cmd(client, message: Message):
    from pyrogram.types import ChatPrivileges
    target = await _get_target(message)
    if not target:
        return await edel(message, "⚠️ Reply ke user yang ingin di-demote.", 5)
    try:
        await client.promote_chat_member(
            message.chat.id, target.id,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_invite_users=False,
                can_pin_messages=False,
            )
        )
        await message.edit(f"⬇️ [{get_name(target)}](tg://user?id={target.id}) di-**demote**.")
    except (ChatAdminRequired, UserAdminInvalid):
        await message.edit("❌ Tidak bisa demote user ini.")
