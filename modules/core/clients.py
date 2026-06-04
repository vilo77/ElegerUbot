"""
Module: clients
Commands: .clients, .client <n>
Show status of all active clients.
"""

from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import uptime_str

MODULE = "clients"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}clients` — Daftar semua client aktif
• `{CMD_HANDLER}client <n>` — Info detail client ke-n
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"clients$")
async def list_clients(client, message: Message):
    """List all active clients."""
    total = len(eleger.CLIENTS)
    lines = [f"👥 **Active Clients: `{total}`**", "━━━━━━━━━━━━━━━━━"]
    for c in eleger.CLIENTS:
        me = c._me
        if me:
            uname = f"@{me.username}" if me.username else "no username"
            premium = "⭐" if getattr(me, "is_premium", False) else ""
            lines.append(
                f"[**{c.client_index}**] [{me.first_name}](tg://user?id={me.id}) {premium}\n"
                f"  `{me.id}` · {uname}"
            )
        else:
            lines.append(f"[**{c.client_index}**] _(not started)_")
    lines.append("━━━━━━━━━━━━━━━━━")
    lines.append(f"⏱ **Uptime:** `{uptime_str(eleger.START_TIME)}`")
    await message.edit("\n".join(lines), disable_web_page_preview=True)


@eleger_cmd(r"client (\d+)$")
async def client_detail(client, message: Message):
    """Show detail for a specific client."""
    idx = int(message.matches[0].group(1))
    if idx < 1 or idx > len(eleger.CLIENTS):
        return await message.edit(f"❌ Client #{idx} tidak ada. Total: `{len(eleger.CLIENTS)}`")

    c = eleger.CLIENTS[idx - 1]
    me = c._me
    if not me:
        return await message.edit(f"❌ Client #{idx} belum aktif.")

    uname = f"@{me.username}" if me.username else "–"
    premium = "⭐ Ya" if getattr(me, "is_premium", False) else "Tidak"
    verified = "✅ Ya" if me.is_verified else "Tidak"
    bot = "🤖 Ya" if me.is_bot else "Tidak"
    dc = getattr(me, "dc_id", "–")

    text = (
        f"📱 **Client #{idx} Detail**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 **Nama:** [{me.first_name}](tg://user?id={me.id})\n"
        f"🆔 **ID:** `{me.id}`\n"
        f"📛 **Username:** {uname}\n"
        f"📡 **DC ID:** `{dc}`\n"
        f"⭐ **Premium:** {premium}\n"
        f"✅ **Verified:** {verified}\n"
        f"🤖 **Bot:** {bot}"
    )
    await message.edit(text, disable_web_page_preview=True)
