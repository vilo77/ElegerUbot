"""
Core decorators for ElegerUbot.

Usage in modules:
    from eleger.helpers import eleger_cmd

    @eleger_cmd("ping$")
    async def ping_cmd(client, message):
        await message.edit("🏓 Pong!")
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from typing import Callable

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, EditedMessageHandler, RawUpdateHandler
from pyrogram.handlers.chat_member_updated_handler import ChatMemberUpdatedHandler
from pyrogram import raw

import eleger
from eleger import CMD_HANDLER, SUDO_HANDLER, CMD_HELP, LOADED_MODULES

LOGS = logging.getLogger("eleger.decorator")


def _make_pattern_filter(pattern: str, handler: str) -> filters.Filter:
    """Build a regex filter for a command pattern with the given handler prefix."""
    import re
    prefix = re.escape(handler)
    regex = rf"^{prefix}{pattern}"
    return filters.regex(regex)


def eleger_cmd(
    pattern: str,
    *,
    allow_sudo: bool = True,
    group_only: bool = False,
    private_only: bool = False,
    admin_only: bool = False,
    disable_edited: bool = False,
    allow_channels: bool = False,
    group: int = 0,
):
    """
    Register a command handler on ALL active clients.

    @eleger_cmd("ping$")
    async def ping(client, message): ...
    """
    def decorator(func: Callable):
        owner_filter = _make_pattern_filter(pattern, CMD_HANDLER) & filters.me
        sudo_filter = _make_pattern_filter(pattern, SUDO_HANDLER)

        # Build chat-type restriction filter
        chat_filter = filters.all
        if group_only:
            chat_filter = filters.group
        elif private_only:
            chat_filter = filters.private

        async def _wrapper(client: Client, message):
            # Skip channels unless explicitly allowed
            if not allow_channels and message.chat and message.chat.type.name == "CHANNEL":
                return
            # Admin-only check
            if admin_only:
                if message.chat.type.name in ("PRIVATE",):
                    return await message.edit("⚠️ This command is for groups only.")
                member = await client.get_chat_member(message.chat.id, message.from_user.id)
                if member.status.name not in ("ADMINISTRATOR", "OWNER"):
                    return await message.edit("⛔ Admins only.")
            try:
                await func(client, message)
            except asyncio.CancelledError:
                pass
            except Exception:
                LOGS.error(f"Error in {func.__name__}:\n{traceback.format_exc()}")

        # Register on a specific client
        def _register_on_client(c: Client):
            # Owner handler (outgoing)
            c.add_handler(
                MessageHandler(_wrapper, owner_filter & chat_filter),
                group=group,
            )
            if not disable_edited:
                c.add_handler(
                    EditedMessageHandler(_wrapper, owner_filter & chat_filter),
                    group=group,
                )
            # Sudo handler (incoming from sudo users)
            if allow_sudo and eleger.SUDO_USERS:
                sudo_id_filter = filters.user(list(eleger.SUDO_USERS))
                c.add_handler(
                    MessageHandler(_wrapper, sudo_filter & sudo_id_filter & chat_filter),
                    group=group,
                )
                if not disable_edited:
                    c.add_handler(
                        EditedMessageHandler(_wrapper, sudo_filter & sudo_id_filter & chat_filter),
                        group=group,
                    )

        # Store registration callback
        _PENDING_HANDLERS.append(_register_on_client)

        # Track command in help registry
        short_name = func.__module__.split(".")[-1]
        _MODULE_CMDS.setdefault(short_name, []).append(pattern)

        func._is_eleger_cmd = True
        return func

    return decorator


def sudo_cmd(pattern: str, group: int = 0):
    """Register a handler only for SUDO_USERS (incoming messages)."""
    def decorator(func: Callable):
        sudo_filter = _make_pattern_filter(pattern, SUDO_HANDLER)

        async def _wrapper(client: Client, message):
            try:
                await func(client, message)
            except Exception:
                LOGS.error(traceback.format_exc())

        def _register(c: Client):
            if not eleger.SUDO_USERS:
                return
            sudo_id_filter = filters.user(list(eleger.SUDO_USERS))
            c.add_handler(
                MessageHandler(_wrapper, sudo_filter & sudo_id_filter),
                group=group,
            )

        _PENDING_HANDLERS.append(_register)
        return func

    return decorator


def on_action(group: int = 0):
    """Register a ChatAction handler on all clients."""
    def decorator(func: Callable):
        def _register(c: Client):
            from pyrogram.handlers import ChatMemberUpdatedHandler
            c.add_handler(ChatMemberUpdatedHandler(func), group=group)
        _PENDING_HANDLERS.append(_register)
        return func
    return decorator


def on_raw(group: int = 0):
    """Register a raw update handler on all clients."""
    def decorator(func: Callable):
        def _register(c: Client):
            c.add_handler(RawUpdateHandler(func), group=group)
        _PENDING_HANDLERS.append(_register)
        return func
    return decorator


# Internal registry — populated during module load, flushed by __main__
_PENDING_HANDLERS: list[Callable] = []
_MODULE_CMDS: dict[str, list[str]] = {}


def apply_handlers_to_client(client: Client):
    """Apply all pending handler registrations to a single client."""
    for reg_fn in _PENDING_HANDLERS:
        try:
            reg_fn(client)
        except Exception:
            LOGS.error(traceback.format_exc())

def flush_handlers():
    """Apply handlers to all currently registered clients. Run AFTER clients are started."""
    LOGS.info(f"Registering {len(_PENDING_HANDLERS)} handlers on {len(eleger.CLIENTS)} client(s)...")
    for c in eleger.CLIENTS:
        apply_handlers_to_client(c)
    LOGS.info("All handlers registered.")
