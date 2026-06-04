"""
Module: misc (fun)
Commands: .tr, .tts, .carbon, .quote
"""

import os
import urllib.parse
import aiohttp
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER, DOWNLOADS_DIR
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "misc"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}tr <lang> [teks]` — Terjemahkan teks (reply atau inline)
• `{CMD_HANDLER}tts <teks>` — Text-to-speech (Google TTS)
• `{CMD_HANDLER}carbon` — Buat screenshot kode karbon (reply code)
• `{CMD_HANDLER}quote` — Quote pesan jadi gambar
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"tr ([a-z]{2})(?: (.+))?$")
async def translate_cmd(client, message: Message):
    """Translate text using MyMemory API."""
    lang = message.matches[0].group(1)
    text = message.matches[0].group(2)

    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption

    if not text:
        return await edel(message, "⚠️ Berikan teks atau reply ke pesan.", 5)

    await message.edit("`🌐 Menerjemahkan...`")
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text[:500], "langpair": f"auto|{lang}"}
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
        result = data["responseData"]["translatedText"]
        await message.edit(
            f"🌐 **Terjemahan → `{lang}`**\n\n"
            f"**Asli:** `{text[:200]}`\n\n"
            f"**Hasil:** `{result}`"
        )
    except Exception as e:
        await message.edit(f"❌ Error terjemah: `{e}`")


@eleger_cmd(r"tts (.+)")
async def tts_cmd(client, message: Message):
    """Google Text-to-Speech."""
    text = message.matches[0].group(1).strip()
    await message.edit("`🔊 Membuat audio...`")

    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(text)}&tl=id&client=tw-ob"
    out_path = DOWNLOADS_DIR / "tts.mp3"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return await message.edit("❌ Gagal mengambil audio TTS.")
                out_path.write_bytes(await resp.read())
        await message.delete()
        await client.send_voice(message.chat.id, str(out_path), caption=f"🔊 TTS: `{text[:100]}`")
    except Exception as e:
        await message.edit(f"❌ Error TTS: `{e}`")
    finally:
        if out_path.exists():
            out_path.unlink()


@eleger_cmd(r"carbon$")
async def carbon_cmd(client, message: Message):
    """Generate code screenshot via Carbon API."""
    reply = message.reply_to_message
    if not reply:
        return await edel(message, "⚠️ Balas ke pesan berisi kode.", 5)

    code = reply.text or reply.caption
    if not code:
        return await edel(message, "⚠️ Tidak ada teks pada pesan itu.", 5)

    await message.edit("`⏳ Membuat gambar kode...`")
    url = "https://carbonara.solopov.dev/api/cook"
    payload = {"code": code}
    out_path = DOWNLOADS_DIR / "carbon.png"
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    return await message.edit("❌ Gagal membuat gambar Carbon.")
                out_path.write_bytes(await resp.read())
        await message.delete()
        await client.send_photo(
            message.chat.id,
            str(out_path),
            caption="📸 **Code Screenshot** via Carbon"
        )
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
    finally:
        if out_path.exists():
            out_path.unlink()


@eleger_cmd(r"quote$")
async def quote_cmd(client, message: Message):
    """Get replied message info as a formatted quote."""
    reply = message.reply_to_message
    if not reply:
        return await edel(message, "⚠️ Balas ke pesan yang ingin di-quote.", 5)

    sender = reply.from_user
    name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() if sender else "Unknown"
    text = reply.text or reply.caption or "[media]"

    quote_text = (
        f"💬 **Quote**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 **{name}**\n"
        f"> {text[:400]}\n"
        f"━━━━━━━━━━━━━━━━━"
    )
    await message.edit(quote_text)
