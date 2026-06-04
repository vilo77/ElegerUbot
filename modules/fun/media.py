"""
Module: media
Commands: .dl, .upload, .docx
"""

import os
import time
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER, DOWNLOADS_DIR
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel, progress, human_size

MODULE = "media"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}dl` — Download media dari pesan yang direply
• `{CMD_HANDLER}upload <path>` — Upload file dari path lokal
• `{CMD_HANDLER}mediainfo` — Info detail media yang direply
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"dl$")
async def download_media_cmd(client, message: Message):
    """Download replied message media to server."""
    reply = message.reply_to_message
    if not reply or not (reply.media or reply.document or reply.photo or reply.video or reply.audio or reply.voice):
        return await edel(message, "⚠️ Balas ke pesan berisi media.", 5)

    await message.edit("`⬇️ Mulai mengunduh...`")
    start = time.time()

    async def _prog(current, total):
        await progress(current, total, message, start, "⬇️ Mengunduh")

    try:
        path = await client.download_media(
            reply,
            file_name=str(DOWNLOADS_DIR) + "/",
            progress=_prog,
        )
        elapsed = time.time() - start
        size = os.path.getsize(path)
        await message.edit(
            f"✅ **Download Selesai!**\n"
            f"📁 **File:** `{os.path.basename(path)}`\n"
            f"📦 **Size:** `{human_size(size)}`\n"
            f"⏱ **Waktu:** `{elapsed:.1f}s`\n"
            f"📂 **Path:** `{path}`"
        )
    except Exception as e:
        await message.edit(f"❌ Download gagal: `{e}`")


@eleger_cmd(r"upload (.+)")
async def upload_file_cmd(client, message: Message):
    """Upload a local file to current chat."""
    file_path = message.matches[0].group(1).strip()
    if not os.path.exists(file_path):
        return await message.edit(f"❌ File tidak ditemukan: `{file_path}`")

    size = os.path.getsize(file_path)
    await message.edit(f"`⬆️ Mengupload {os.path.basename(file_path)} ({human_size(size)})...`")
    start = time.time()

    async def _prog(current, total):
        await progress(current, total, message, start, "⬆️ Mengupload")

    try:
        await client.send_document(
            message.chat.id,
            file_path,
            caption=f"📤 `{os.path.basename(file_path)}`",
            progress=_prog,
        )
        await message.delete()
    except Exception as e:
        await message.edit(f"❌ Upload gagal: `{e}`")


@eleger_cmd(r"mediainfo$")
async def mediainfo_cmd(client, message: Message):
    """Show media metadata of replied message."""
    reply = message.reply_to_message
    if not reply:
        return await edel(message, "⚠️ Balas ke pesan berisi media.", 5)

    lines = ["📊 **Media Info**", "━━━━━━━━━━━━━━━━━"]

    if reply.photo:
        p = reply.photo
        lines += [f"📷 **Type:** Foto", f"📐 **Size:** `{p.width}x{p.height}`", f"📦 **File Size:** `{human_size(p.file_size)}`", f"🆔 **File ID:** `{p.file_id}`"]
    elif reply.video:
        v = reply.video
        lines += [f"🎬 **Type:** Video", f"📐 **Size:** `{v.width}x{v.height}`", f"⏱ **Duration:** `{v.duration}s`", f"📦 **File Size:** `{human_size(v.file_size)}`", f"🎞 **MIME:** `{v.mime_type}`", f"🆔 **File ID:** `{v.file_id}`"]
    elif reply.audio:
        a = reply.audio
        lines += [f"🎵 **Type:** Audio", f"🎤 **Performer:** `{a.performer or '–'}`", f"🎼 **Title:** `{a.title or '–'}`", f"⏱ **Duration:** `{a.duration}s`", f"📦 **File Size:** `{human_size(a.file_size)}`", f"🆔 **File ID:** `{a.file_id}`"]
    elif reply.document:
        d = reply.document
        lines += [f"📄 **Type:** Dokumen", f"📛 **Name:** `{d.file_name or '–'}`", f"🎞 **MIME:** `{d.mime_type}`", f"📦 **File Size:** `{human_size(d.file_size)}`", f"🆔 **File ID:** `{d.file_id}`"]
    elif reply.sticker:
        s = reply.sticker
        lines += [f"🎭 **Type:** Stiker", f"😊 **Emoji:** `{s.emoji or '–'}`", f"📦 **Set:** `{s.set_name or '–'}`", f"📐 **Size:** `{s.width}x{s.height}`", f"🆔 **File ID:** `{s.file_id}`"]
    elif reply.voice:
        vo = reply.voice
        lines += [f"🎙 **Type:** Voice", f"⏱ **Duration:** `{vo.duration}s`", f"📦 **File Size:** `{human_size(vo.file_size)}`", f"🆔 **File ID:** `{vo.file_id}`"]
    else:
        return await edel(message, "❌ Tidak ada media yang dikenali.", 5)

    await message.edit("\n".join(lines))
