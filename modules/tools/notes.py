"""
Module: notes
Commands: .save, .get, .notes, .clear
"""

import json
from pathlib import Path
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER, DATA_DIR
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "notes"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}save <nama> <teks>` — Simpan catatan
• `{CMD_HANDLER}get <nama>` — Ambil catatan
• `{CMD_HANDLER}notes` — Daftar semua catatan
• `{CMD_HANDLER}clear <nama>` — Hapus catatan
• `{CMD_HANDLER}clearall` — Hapus semua catatan (milik chat ini)
"""
eleger.CMD_HELP[MODULE] = HELP

_NOTES_FILE = DATA_DIR / "notes.json"


def _load() -> dict:
    if _NOTES_FILE.exists():
        try:
            return json.loads(_NOTES_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(data: dict):
    _NOTES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _key(chat_id: int, name: str) -> str:
    return f"{chat_id}:{name.lower()}"


@eleger_cmd(r"save (.+)")
async def save_note(client, message: Message):
    args = message.matches[0].group(1).strip().split(None, 1)
    if len(args) < 2:
        return await edel(message, "⚠️ Format: `.save <nama> <teks>`", 5)
    name, text = args[0], args[1]
    data = _load()
    key = _key(message.chat.id, name)
    data[key] = text
    _save(data)
    await message.edit(f"✅ Catatan **`{name}`** disimpan.")


@eleger_cmd(r"get (.+)")
async def get_note(client, message: Message):
    name = message.matches[0].group(1).strip()
    data = _load()
    key = _key(message.chat.id, name)
    if key not in data:
        return await edel(message, f"❌ Catatan `{name}` tidak ditemukan.", 5)
    await message.edit(f"📝 **{name}:**\n{data[key]}")


@eleger_cmd(r"notes$")
async def list_notes(client, message: Message):
    data = _load()
    chat_prefix = f"{message.chat.id}:"
    keys = [k.split(":", 1)[1] for k in data if k.startswith(chat_prefix)]
    if not keys:
        return await message.edit("📭 Tidak ada catatan di chat ini.")
    text = "📚 **Catatan tersimpan:**\n" + "\n".join(f"• `{k}`" for k in sorted(keys))
    await message.edit(text)


@eleger_cmd(r"clear (.+)")
async def clear_note(client, message: Message):
    name = message.matches[0].group(1).strip()
    data = _load()
    key = _key(message.chat.id, name)
    if key not in data:
        return await edel(message, f"❌ Catatan `{name}` tidak ada.", 5)
    del data[key]
    _save(data)
    await message.edit(f"🗑 Catatan **`{name}`** dihapus.")


@eleger_cmd(r"clearall$")
async def clear_all_notes(client, message: Message):
    data = _load()
    chat_prefix = f"{message.chat.id}:"
    to_del = [k for k in data if k.startswith(chat_prefix)]
    for k in to_del:
        del data[k]
    _save(data)
    await message.edit(f"🗑 **{len(to_del)}** catatan dihapus dari chat ini.")
