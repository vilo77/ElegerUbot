from __future__ import annotations
import asyncio
import eleger
from eleger import (API_ID, API_HASH, BOT_TOKEN, SESSION_STRINGS, BOT_NAME, BOT_VERSION, LOG_CHAT, LOGS)
from eleger.client import ElegerClient
from eleger.loader import load_all_modules
from eleger.helpers.decorator import flush_handlers
from eleger.helpers.logger import send_log
from pathlib import Path
from pyrogram import Client

async def startup():
    LOGS.info(f"⚡ Starting {BOT_NAME}...")

    # 1. Init Assistant Bot (PENTING: Harus sebelum load_all_modules)
    if BOT_TOKEN:
        try:
            eleger.assistant = Client(
                "assistant_bot",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                in_memory=True
            )
            await eleger.assistant.start()
            LOGS.info("✅ Assistant Bot started & registered!")
        except Exception as e:
            LOGS.error(f"❌ Gagal menyalakan Assistant Bot: {e}")

    # 2. Build Clients
    for idx, ss in enumerate(SESSION_STRINGS, start=1):
        client = ElegerClient(client_index=idx, session_string=ss, api_id=API_ID, api_hash=API_HASH)
        eleger.CLIENTS.append(client)

    # 3. Load Modules
    base_dir = Path(__file__).parent
    success, failed = load_all_modules(base_dir)
    eleger.LOADED_MODULES.extend(success)
    LOGS.info(f"Modules loaded: {len(success)} OK, {len(failed)} FAILED")

    # 4. Start Clients & Flush Handlers
    await asyncio.gather(*[c.start() for c in eleger.CLIENTS])
    flush_handlers() 

    LOGS.info("✅ ElegerUbot is running!")

async def main():
    await startup()
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
