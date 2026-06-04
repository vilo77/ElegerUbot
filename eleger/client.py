"""
ElegerClient — Extended Pyrogram Client with multi-client utilities.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from pyrogram import Client
import pyromod.listen  # Patches pyrogram Client with .ask()

if TYPE_CHECKING:
    from pyrogram.types import User

LOGS = logging.getLogger("eleger.client")


class ElegerClient(Client):
    """
    Extended Pyrogram Client.
    Stores client index (1-based) and cached `me` info.
    """

    def __init__(self, client_index: int, session_string: str, api_id: int, api_hash: str):
        super().__init__(
            name=f"eleger_{client_index}",
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            in_memory=True,
            sleep_threshold=60,
        )
        self.client_index: int = client_index
        self._me: "User | None" = None

    async def get_me_cached(self) -> "User":
        if self._me is None:
            self._me = await self.get_me()
        return self._me

    async def start(self):
        await super().start()
        self._me = await self.get_me()
        LOGS.info(
            f"[Client {self.client_index}] Logged in as "
            f"{self._me.first_name} (ID: {self._me.id})"
        )
        return self

    def __repr__(self) -> str:
        name = self._me.first_name if self._me else "?"
        return f"<ElegerClient #{self.client_index} — {name}>"
