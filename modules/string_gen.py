import os
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd

# Database sederhana
ALLOWED_USERS = set()
ADMIN_ID = 603427690 
GEN_STATE = {} # Format: {user_id: {"client": ..., "phone": ..., "hash": ...}}

MODULE = "string_gen"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}allow [reply/id]` — Memberi akses ke user lain.
• `/gen [nomor]` — (Via Assistant Bot) Mulai generate.
• `/otp [kode]` — (Via Assistant Bot) Input OTP (Wajib spasi).
• `/pw [password]` — (Via Assistant Bot) Input password 2FA.
"""
eleger.CMD_HELP[MODULE] = HELP

# --- 1. FITUR IZIN AKSES (Via Userbot) ---
@eleger_cmd(r"allow(?: (.+))?$", allow_sudo=False)
async def allow_access(client, message):
    if message.from_user.id != ADMIN_ID: return
    
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        target_id = int(message.command[1])
    else:
        return await message.edit("❌ Reply pesan user atau masukkan ID.")
        
    ALLOWED_USERS.add(target_id)
    await message.edit(f"✅ User `{target_id}` diizinkan akses `/gen`")

# --- 2. FITUR GEN (Via Assistant Bot) ---
@eleger.assistant.on_message(filters.command(["gen", "otp", "pw"]))
async def assistant_gen(client, message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID and user_id not in ALLOWED_USERS:
        return await message.reply("⛔ **Akses ditolak.** Hubungi Admin.")

    cmd = message.command[0]
    api_id = int(os.environ.get("API_ID", 6))
    api_hash = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")

    # PROSES GEN
    if cmd == "gen":
        if len(message.command) < 2: return await message.reply("❌ Format: `/gen +628xxx`")
        phone = message.command[1]
        
        # Bersihkan sesi lama jika ada
        if user_id in GEN_STATE:
            await GEN_STATE[user_id]["client"].disconnect()
            
        temp_client = Client(f"gen_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True)
        await temp_client.connect()
        try:
            sent = await temp_client.send_code(phone)
            GEN_STATE[user_id] = {"client": temp_client, "phone": phone, "hash": sent.phone_code_hash}
            await message.reply("✅ OTP terkirim. Gunakan `/otp 1 2 3 4 5`")
        except Exception as e:
            await temp_client.disconnect()
            await message.reply(f"❌ Eror: {str(e)}")

    # PROSES OTP
    elif cmd == "otp":
        if user_id not in GEN_STATE: return await message.reply("Gunakan `/gen` dulu.")
        code = message.command[1].replace(" ", "")
        state = GEN_STATE[user_id]
        try:
            await state["client"].sign_in(state["phone"], state["hash"], code)
            session = await state["client"].export_session_string()
            await message.reply(f"🎉 **Sukses!**\n\n`{session}`")
            await state["client"].disconnect()
            del GEN_STATE[user_id]
        except SessionPasswordNeeded:
            await message.reply("🔐 Perlu password 2FA. Gunakan `/pw sandi`")
        except Exception as e:
            await message.reply(f"❌ Eror: {str(e)}")

    # PROSES PASSWORD
    elif cmd == "pw":
        if user_id not in GEN_STATE: return await message.reply("Gunakan `/gen` dulu.")
        password = message.command[1]
        state = GEN_STATE[user_id]
        try:
            await state["client"].check_password(password)
            session = await state["client"].export_session_string()
            await message.reply(f"🎉 **Sukses!**\n\n`{session}`")
            await state["client"].disconnect()
            del GEN_STATE[user_id]
        except Exception as e:
            await message.reply(f"❌ Password salah: {str(e)}")
