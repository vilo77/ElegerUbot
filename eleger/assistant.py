"""
Assistant Bot handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message

import eleger
from eleger import API_ID, API_HASH, OWNER_ID
from eleger.client import ElegerClient
from eleger.helpers.decorator import apply_handlers_to_client
from eleger.helpers.logger import send_log

def init_assistant():
    if not eleger.ASSISTANT:
        return

    assistant: Client = eleger.ASSISTANT

    # Only allow owner to use the assistant
    owner_filter = filters.user(OWNER_ID) if OWNER_ID else filters.all

    @assistant.on_message(filters.command("start") & owner_filter)
    async def start_cmd(client: Client, message: Message):
        await message.reply(
            f"👋 **Halo!** Saya adalah Assistant Bot untuk {eleger.BOT_NAME}.\n"
            f"Ketik `/clients` untuk melihat status klien.\n"
            f"Ketik `/addclient <session_string>` untuk menambah klien secara instan."
        )

    @assistant.on_message(filters.command("clients") & owner_filter)
    async def clients_cmd(client: Client, message: Message):
        total = len(eleger.CLIENTS)
        lines = [f"👥 **Active Clients: `{total}`**", "━━━━━━━━━━━━━━━━━"]
        for c in eleger.CLIENTS:
            me = c._me
            if me:
                uname = f"@{me.username}" if me.username else "no username"
                lines.append(f"[**{c.client_index}**] {me.first_name} (`{me.id}`) — {uname}")
            else:
                lines.append(f"[**{c.client_index}**] _(not started)_")
        await message.reply("\n".join(lines))

    @assistant.on_message(filters.command("addclient") & owner_filter)
    async def addclient_cmd(client: Client, message: Message):
        if len(message.command) < 2:
            return await message.reply("⚠️ Format salah! Gunakan: `/addclient <session_string>`")
        
        session_string = message.command[1].strip()
        idx = len(eleger.CLIENTS) + 1

        msg = await message.reply(f"⏳ **Menambahkan Client #{idx}...**")

        try:
            new_client = ElegerClient(
                client_index=idx,
                session_string=session_string,
                api_id=API_ID,
                api_hash=API_HASH,
            )
            await new_client.start()
            
            # Apply all existing modules/handlers to this new client
            apply_handlers_to_client(new_client)
            
            eleger.CLIENTS.append(new_client)
            eleger.SESSION_STRINGS.append(session_string)
            
            me = new_client._me
            await msg.edit(
                f"✅ **Client #{idx} Berhasil Dideploy!**\n"
                f"👤 Nama: {me.first_name}\n"
                f"🆔 ID: `{me.id}`\n\n"
                f"⚠️ *Catatan: Penambahan ini bersifat in-memory. Jika bot ter-restart, "
                f"client ini akan hilang kecuali session string-nya juga ditambahkan ke Environment Variables (misal Railway).* "
            )
            await send_log("Deploy Logs", f"✅ Client #{idx} ({me.first_name} - `{me.id}`) berhasil dideploy via Assistant.")
        except Exception as e:
            await msg.edit(f"❌ **Gagal menambahkan client!**\nError: `{e}`")

    eleger.LOGS.info("Assistant Bot handlers initialized.")
