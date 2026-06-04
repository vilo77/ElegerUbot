"""
Forum-based Topic Logger
"""

import json
import logging
import traceback
import asyncio
from pathlib import Path

from pyrogram.errors import FloodWait

import eleger
from eleger import LOG_CHAT, DATA_DIR, LOGS

_TOPICS_FILE = DATA_DIR / "topics.json"
_TOPICS_CACHE: dict[str, int] = {}

def _load_topics():
    if _TOPICS_FILE.exists():
        try:
            data = json.loads(_TOPICS_FILE.read_text())
            _TOPICS_CACHE.update(data)
        except Exception as e:
            LOGS.warning(f"Failed to load topics.json: {e}")

def _save_topics():
    try:
        _TOPICS_FILE.write_text(json.dumps(_TOPICS_CACHE, indent=2))
    except Exception as e:
        LOGS.warning(f"Failed to save topics.json: {e}")

_load_topics()

async def get_or_create_topic(topic_name: str) -> int | None:
    """Get the message_thread_id for a given topic name. Creates it if it doesn't exist."""
    if not LOG_CHAT:
        return None

    # Use the assistant if available, else first client
    client = eleger.ASSISTANT if eleger.ASSISTANT else (eleger.CLIENTS[0] if eleger.CLIENTS else None)
    if not client:
        return None

    if topic_name in _TOPICS_CACHE:
        return _TOPICS_CACHE[topic_name]

    try:
        topic = await client.create_forum_topic(LOG_CHAT, title=topic_name)
        _TOPICS_CACHE[topic_name] = topic.id
        _save_topics()
        return topic.id
    except Exception as e:
        LOGS.error(f"Failed to create forum topic '{topic_name}': {e}")
        return None

async def send_log(topic_name: str, text: str):
    """Send a log message to a specific topic in the LOG_CHAT."""
    if not LOG_CHAT:
        return

    client = eleger.ASSISTANT if eleger.ASSISTANT else (eleger.CLIENTS[0] if eleger.CLIENTS else None)
    if not client:
        return

    thread_id = await get_or_create_topic(topic_name)
    
    try:
        await client.send_message(
            LOG_CHAT,
            text,
            reply_to_message_id=thread_id,
            disable_web_page_preview=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(
            LOG_CHAT,
            text,
            reply_to_message_id=thread_id,
            disable_web_page_preview=True
        )
    except Exception as e:
        LOGS.error(f"Failed to send log to topic '{topic_name}': {e}")
