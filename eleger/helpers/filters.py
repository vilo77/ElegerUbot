"""
Custom Pyrogram filters for ElegerUbot.
"""

from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message

import eleger


def is_owner(_, __, message: Message) -> bool:
    """True if message sender is the bot owner (first client's user ID)."""
    if not eleger.CLIENTS:
        return False
    owner_ids = {c._me.id for c in eleger.CLIENTS if c._me}
    uid = message.from_user.id if message.from_user else None
    return uid in owner_ids


def is_sudo(_, __, message: Message) -> bool:
    """True if sender is in SUDO_USERS."""
    uid = message.from_user.id if message.from_user else None
    if uid is None:
        return False
    return uid in eleger.SUDO_USERS


# Register as Pyrogram custom filters
is_owner = filters.create(is_owner, "IsOwnerFilter")
is_sudo = filters.create(is_sudo, "IsSudoFilter")
