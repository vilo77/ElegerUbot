from pyrogram import Client, filters
import asyncio

@Client.on_message(filters.command("updatepeers", prefixes=".") & filters.me)
async def update_peers(client, message):
    # Mengirim pesan status awal
    msg = await message.reply_text("🔄 **Sedang memindai dan menyimpan daftar peers...**\n*Proses ini mungkin memakan waktu beberapa detik, mohon tunggu.*")
    
    count = 0
    try:
        # get_dialogs() akan memaksa Pyrogram membaca semua obrolan 
        # dan otomatis menyimpannya ke dalam cache/database internal
        async for dialog in client.get_dialogs():
            count += 1
            
        # Mengubah pesan awal menjadi pesan sukses
        await msg.edit_text(f"✅ **Update Peers Selesai!**\nBerhasil memindai dan menyimpan **{count}** obrolan (Grup/Channel/Kontak) ke dalam memori bot.")
        
    except Exception as e:
        # Jika ada eror saat memindai
        await msg.edit_text(f"❌ **Terjadi kesalahan:**\n`{str(e)}`")
