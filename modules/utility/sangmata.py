import asyncio
from pyrogram import Client, filters
from pyrogram.errors import YouBlockedUser

@Client.on_message(filters.command(["sg", "sangmata"], prefixes=".") & filters.me)
async def cek_sangmata(client, message):
    # Mengambil ID target (dari Reply atau Username)
    target = ""
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        target = message.command[1]
    else:
        return await message.edit_text("❌ **Gagal:** Silakan *reply* (balas) pesan target atau ketik `.sg @username`")

    msg = await message.edit_text("🔍 **Sedang melacak riwayat target di database SangMata...**")
    bot_target = "SangMataInfo_bot"

    try:
        # Buka blokir bot jika tidak sengaja terblokir
        try:
            await client.unblock_user(bot_target)
        except:
            pass
        
        # Kirim ID target ke SangMata
        await client.send_message(bot_target, f"{target}")
        
        # Tunggu 3 detik agar bot SangMata pusat selesai mengetik & membalas
        await asyncio.sleep(3)
        
        # Mengambil 2 balasan terakhir dari bot SangMata
        hasil = []
        async for chat_bot in client.get_chat_history(bot_target, limit=2):
            if chat_bot.text and not chat_bot.text.startswith("Kirimkan"):
                hasil.append(chat_bot.text)
                
        if not hasil:
            return await msg.edit_text("❌ **Tidak ada riwayat nama ditemukan.** (Target mungkin tidak pernah ganti nama, atau server pusat sedang lambat).")
            
        # Gabungkan dan tampilkan hasil
        teks_hasil = "\n\n".join(hasil)
        await msg.edit_text(f"**👁️ Hasil Pelacakan SangMata:**\n\n{teks_hasil}")
        
    except YouBlockedUser:
        await msg.edit_text(f"❌ **Gagal:** Tolong buka blokir `@SangMataInfo_bot` terlebih dahulu.")
    except Exception as e:
        await msg.edit_text(f"❌ **Terjadi Eror:** `{str(e)}`")
