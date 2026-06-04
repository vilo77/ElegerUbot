"""
Module: paste
Commands: .paste, .nekobin
"""

import aiohttp
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "paste"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}paste` — Upload teks ke paste.rs (reply atau inline)
• `{CMD_HANDLER}nekobin` — Upload teks ke nekobin.com
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"paste$")
async def paste_cmd(client, message: Message):
    """Paste text to paste.rs."""
    text = None
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        # Try text after command
        raw = message.text or ""
        parts = raw.split(None, 1)
        text = parts[1] if len(parts) > 1 else None

    if not text:
        return await edel(message, "⚠️ Berikan teks atau reply ke pesan.", 5)

    await message.edit("`⏳ Uploading ke paste.rs...`")
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(
                "https://paste.rs",
                data=text.encode(),
                headers={"Content-Type": "text/plain"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status in (200, 201):
                    url = (await resp.text()).strip()
                    await message.edit(f"📋 **Paste berhasil!**\n🔗 {url}")
                else:
                    await message.edit(f"❌ Gagal upload (HTTP {resp.status})")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@eleger_cmd(r"nekobin$")
async def nekobin_cmd(client, message: Message):
    """Paste text to nekobin.com."""
    text = None
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        raw = message.text or ""
        parts = raw.split(None, 1)
        text = parts[1] if len(parts) > 1 else None

    if not text:
        return await edel(message, "⚠️ Berikan teks atau reply ke pesan.", 5)

    await message.edit("`⏳ Uploading ke nekobin.com...`")
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(
                "https://nekobin.com/api/documents",
                json={"content": text},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()
                if resp.status == 201 and data.get("ok"):
                    key = data["result"]["key"]
                    url = f"https://nekobin.com/{key}"
                    raw_url = f"https://nekobin.com/raw/{key}"
                    await message.edit(
                        f"📋 **Nekobin berhasil!**\n"
                        f"🔗 [View]({url}) · [Raw]({raw_url})"
                    )
                else:
                    await message.edit(f"❌ Gagal upload ke nekobin.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
