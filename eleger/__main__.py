"""
ElegerUbot — Entry point.

Flow:
  1. Build ElegerClient list from SESSION_STRINGS
  2. Load all modules (decorators register _PENDING_HANDLERS)
  3. Start all clients concurrently
  4. Flush pending handlers onto started clients
  5. Send startup notification (optional)
  6. Run until disconnected
"""

from __future__ import annotations

import asyncio
import sys
import logging

import eleger
from eleger import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    SESSION_STRINGS,
    BOT_NAME,
    BOT_VERSION,
    LOG_CHAT,
    START_TIME,
    LOGS,
)
from eleger.client import ElegerClient
from eleger.loader import load_all_modules
from eleger.helpers.decorator import flush_handlers
from eleger.helpers.logger import send_log
from pathlib import Path


async def startup():
    # ── 1. Build clients ──────────────────────────────────────────────────
    LOGS.info(f"╔══════════════════════════════════════╗")
    LOGS.info(f"║  {BOT_NAME} v{BOT_VERSION}  ║")
    LOGS.info(f"╚══════════════════════════════════════╝")
    LOGS.info(f"Initializing {len(SESSION_STRINGS)} client(s)...")

    for idx, ss in enumerate(SESSION_STRINGS, start=1):
        client = ElegerClient(
            client_index=idx,
            session_string=ss,
            api_id=API_ID,
            api_hash=API_HASH,
        )
        eleger.CLIENTS.append(client)

    # ── 2. Load modules (populates _PENDING_HANDLERS) ────────────────────
    base_dir = Path(__file__).parent.parent
    success, failed = load_all_modules(base_dir)
    eleger.LOADED_MODULES.extend(success)
    LOGS.info(f"Modules loaded: {len(success)} OK, {len(failed)} FAILED")
    if failed:
        LOGS.warning("Failed modules: " + ", ".join(failed))

    # ── 3. Start Assistant Bot ───────────────────────────────────────────
    if BOT_TOKEN:
        LOGS.info("Starting Assistant Bot...")
        # pyrefly: ignore [missing-import]
        from pyrogram import Client
        eleger.ASSISTANT = Client(
            "assistant_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True
        )
        await eleger.ASSISTANT.start()

        from eleger import assistant
        assistant.init_assistant()

    # ── 4. Start all clients concurrently ────────────────────────────────
    LOGS.info("Starting clients...")
    await asyncio.gather(*[c.start() for c in eleger.CLIENTS])

    # ── 5. Flush handlers onto running clients ────────────────────────────
    flush_handlers()

    # ── 6. Log startup notification ───────────────────────────────────────
    total = len(eleger.CLIENTS)
    me_list = "\\n".join(
        f"  [{i}] {c._me.first_name} (`{c._me.id}`)"
        for i, c in enumerate(eleger.CLIENTS, 1)
    )
    startup_text = (
        f"⚡ **{BOT_NAME} v{BOT_VERSION} started!**\\n\\n"
        f"**Clients:** `{total}`\\n"
        f"{me_list}\\n\\n"
        f"**Modules:** `{len(success)}`\\n"
        f"**Prefix:** `{eleger.CMD_HANDLER}`"
    )
    LOGS.info(f"\\n{startup_text}")

    if LOG_CHAT:
        await send_log("System Logs", startup_text)

    LOGS.info("✅ ElegerUbot is running. Press Ctrl+C to stop.")


async def shutdown():
    LOGS.info("Shutting down clients...")
    coros = [c.stop() for c in eleger.CLIENTS]
    if eleger.ASSISTANT:
        coros.append(eleger.ASSISTANT.stop())
    await asyncio.gather(*coros, return_exceptions=True)
    LOGS.info("All clients stopped. Goodbye!")


async def main():
    await startup()
    # pyrefly: ignore [missing-import]
    from pyrogram import idle
    await idle()
    await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

