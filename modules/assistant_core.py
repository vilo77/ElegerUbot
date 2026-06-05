import os
import asyncio
from pyrogram import Client
import eleger
from eleger import logger

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start_assistant():
    if not BOT_TOKEN:
        logger.warning("Assistant Bot: BOT_TOKEN tidak ditemukan.")
        return
    
    app = Client(
        "assistant_bot",
        api_id=int(os.environ.get("API_ID", 6)),
        api_hash=os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e"),
        bot_token=BOT_TOKEN
    )
    
    await app.start()
    eleger.assistant = app
    logger.info("✅ Assistant Bot berhasil dijalankan!")

loop = asyncio.get_event_loop()
loop.create_task(start_assistant())
