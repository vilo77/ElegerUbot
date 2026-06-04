"""
Utility helpers for ElegerUbot modules.
"""

from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from typing import Optional

from pyrogram.types import Message

LOGS = logging.getLogger("eleger.utils")


# ─── Message helpers ──────────────────────────────────────────────────────────

async def edit(message: Message, text: str, **kwargs) -> Message:
    """Edit a message safely. Falls back to reply if edit fails."""
    try:
        return await message.edit(text, **kwargs)
    except Exception:
        try:
            return await message.reply(text, **kwargs)
        except Exception as e:
            LOGS.error(f"edit() failed: {e}")
            return message


async def edel(message: Message, text: str, delay: float = 5.0, **kwargs) -> None:
    """Edit a message, then delete it after `delay` seconds."""
    try:
        msg = await message.edit(text, **kwargs)
    except Exception:
        try:
            msg = await message.reply(text, **kwargs)
        except Exception:
            return
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


async def reply_or_edit(message: Message, text: str, **kwargs) -> Message:
    """Edit if outgoing, reply if incoming."""
    if message.outgoing:
        return await edit(message, text, **kwargs)
    return await message.reply(text, **kwargs)


# ─── User/chat info helpers ───────────────────────────────────────────────────

def get_name(user) -> str:
    """Get display name from a Pyrogram User or Chat object."""
    if user is None:
        return "Unknown"
    if hasattr(user, "first_name"):
        parts = [user.first_name or "", user.last_name or ""]
        return " ".join(p for p in parts if p).strip() or str(user.id)
    if hasattr(user, "title"):
        return user.title or str(user.id)
    return str(user)


def mention(user) -> str:
    """Return a Markdown mention link for a user."""
    name = get_name(user)
    uid = user.id if hasattr(user, "id") else 0
    return f"[{name}](tg://user?id={uid})"


# ─── File size helpers ────────────────────────────────────────────────────────

def human_size(num_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    if num_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(num_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(num_bytes / p, 2)
    return f"{s} {size_name[i]}"


# ─── Progress bar ─────────────────────────────────────────────────────────────

def progress_bar(current: int, total: int, length: int = 10) -> str:
    """Return a unicode progress bar string."""
    if total == 0:
        return "▱" * length
    filled = int(length * current / total)
    bar = "▰" * filled + "▱" * (length - filled)
    pct = current * 100 / total
    return f"{bar} {pct:.1f}%"


async def progress(
    current: int,
    total: int,
    message: Message,
    start_time: float,
    action: str = "Processing",
) -> None:
    """Callback for Pyrogram upload/download progress."""
    elapsed = time.time() - start_time
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0
    text = (
        f"**{action}**\n"
        f"{progress_bar(current, total)}\n"
        f"`{human_size(current)}` / `{human_size(total)}`\n"
        f"Speed: `{human_size(int(speed))}/s` · ETA: `{int(eta)}s`"
    )
    try:
        await message.edit(text)
    except Exception:
        pass


# ─── Misc ─────────────────────────────────────────────────────────────────────

def split_list(lst: list, n: int) -> list[list]:
    """Split a list into chunks of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def uptime_str(start: float) -> str:
    """Return human-readable uptime from a start timestamp."""
    secs = int(time.time() - start)
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)
