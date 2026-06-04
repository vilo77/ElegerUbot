"""
Module: profile
Commands: .setname, .setbio, .setpic, .delpic, .username
"""

import os
from pyrogram.types import Message
from pyrogram.errors import UsernameOccupied, UsernameInvalid, PhotoCropSizeSmall

import eleger
from eleger import CMD_HANDLER, DOWNLOADS_DIR
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "profile"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}setname <first> [last]` — Ubah nama profil
• `{CMD_HANDLER}setbio <bio>` — Ubah bio profil
• `{CMD_HANDLER}setpic` — Balas foto → jadikan foto profil
• `{CMD_HANDLER}delpic [n|all]` — Hapus foto profil (default: 1)
• `{CMD_HANDLER}username <nama>` — Ubah username
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"setname (.+)", allow_sudo=False)
async def set_name(client, message: Message):
    name_parts = message.matches[0].group(1).strip().split(None, 1)
    first = name_parts[0]
    last = name_parts[1] if len(name_parts) > 1 else ""
    await client.update_profile(first_name=first, last_name=last)
    await message.edit(f"✅ Nama diubah ke: **{first} {last}**")


@eleger_cmd(r"setbio (.+)", allow_sudo=False)
async def set_bio(client, message: Message):
    bio = message.matches[0].group(1).strip()
    await client.update_profile(bio=bio)
    await message.edit(f"✅ Bio diubah ke:\n`{bio}`")


@eleger_cmd(r"setpic$", allow_sudo=False)
async def set_pic(client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await edel(message, "⚠️ Balas ke sebuah foto.", 5)
    await message.edit("`⬇ Mengunduh foto...`")
    path = await client.download_media(reply.photo, file_name=str(DOWNLOADS_DIR / "pfp_temp.jpg"))
    try:
        await client.set_profile_photo(photo=path)
        await message.edit("✅ **Foto profil berhasil diubah!**")
    except PhotoCropSizeSmall:
        await message.edit("❌ Foto terlalu kecil.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@eleger_cmd(r"delpic(?: (.+))?$", allow_sudo=False)
async def del_pic(client, message: Message):
    arg = message.matches[0].group(1)
    me = client._me
    if arg == "all":
        limit = 0
    elif arg and arg.isdigit():
        limit = int(arg)
    else:
        limit = 1

    await message.edit("`⏳ Menghapus foto profil...`")
    photos = []
    async for photo in client.get_chat_photos("me"):
        photos.append(photo.file_id)
        if limit and len(photos) >= limit:
            break

    if not photos:
        return await message.edit("❌ Tidak ada foto profil.")

    await client.delete_profile_photos(photos)
    await message.edit(f"✅ **{len(photos)}** foto profil dihapus.")


@eleger_cmd(r"username (.+)", allow_sudo=False)
async def set_username(client, message: Message):
    uname = message.matches[0].group(1).strip().lstrip("@")
    try:
        await client.update_username(uname)
        await message.edit(f"✅ Username diubah ke: `@{uname}`")
    except UsernameOccupied:
        await message.edit("❌ Username sudah digunakan.")
    except UsernameInvalid:
        await message.edit("❌ Username tidak valid.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
