import os
from pyrogram import filters
from pyrogram.errors import SessionPasswordNeeded
from pyrogram import Client
import eleger
from eleger import CMD_HANDLER

# --- KTP MODUL ---
MODULE = "string_gen"
HELP = f"""
**Plugin:** `{MODULE}` (Via Assistant Bot)

• `/gen [nomor]` — Mulai generate string session.
• `/otp [kode]` — Input OTP (Gunakan spasi: 1 2 3 4 5).
• `/pw [password]` — Input password 2FA (Jika ada).
"""

# Daftarkan KTP ke sistem Eleger
eleger.CMD_HELP[MODULE] = HELP

GEN_STATE = {}

@eleger.assistant.on_message(filters.command(["gen", "otp", "pw"]))
async def assistant_gen(client, message):
    user_id = message.from_user.id
    cmd = message.command[0]
    
    api_id = int(os.environ.get("API_ID", 6))
    api_hash = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")

    if cmd == "gen":
        if len(message.command) < 2: return await message.reply("❌ Format: `/gen +628xxx`")
        phone = message.command[1]
        
        # Bersihkan sesi jika user melakukan generate ulang
        if user_id in GEN_STATE:
            try: await GEN_STATE[user_id]["client"].disconnect()
            except: pass

        temp_client = Client(f"gen_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True)
        await temp_client.connect()
        try:
            sent = await temp_client.send_code(phone)
            GEN_STATE[user_id] = {"client": temp_client, "phone": phone, "hash": sent.phone_code_hash}
            await message.reply("✅ OTP terkirim. Gunakan `/otp 1 2 3 4 5`")
        except Exception as e:
            await temp_client.disconnect()
            await message.reply(f"❌ Eror: {str(e)}")

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
