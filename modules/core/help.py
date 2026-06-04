"""
Module: help
Commands: .help, .cmds
"""

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from pyrogram.types import Message

MODULE = "help"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}help` — Daftar semua modul yang dimuat
• `{CMD_HANDLER}help <modul>` — Info detail sebuah modul
• `{CMD_HANDLER}cmds` — Sama dengan help
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"(help|cmds)(?: (.+))?$")
async def help_cmd(client, message: Message):
    """Show loaded modules or detail a specific module."""
    args = message.matches[0].group(2)

    if args:
        name = args.strip().lower()
        doc = eleger.CMD_HELP.get(name)
        if doc:
            await message.edit(doc)
        else:
            modules_str = ", ".join(f"`{m}`" for m in sorted(eleger.CMD_HELP))
            await message.edit(
                f"❌ Module `{name}` tidak ditemukan.\n\n"
                f"**Modules tersedia:**\n{modules_str}"
            )
        return

    # List all modules
    modules = sorted(eleger.CMD_HELP.keys())
    total = len(modules)
    rows = [f"• `{m}`" for m in modules]
    # Split into 2 columns visually
    half = (total + 1) // 2
    col1 = rows[:half]
    col2 = rows[half:]
    paired = [
        f"{a:<30} {b}" if i < len(col2) else a
        for i, (a, b) in enumerate(zip(col1, col2 + [""] * len(col1)))
    ]

    text = (
        f"📚 **{eleger.BOT_NAME} — Help Menu**\n"
        f"**Prefix:** `{CMD_HANDLER}` · **Modules:** `{total}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        + "\n".join(f"• `{m}`" for m in modules)
        + f"\n━━━━━━━━━━━━━━━━━\n"
        f"Ketik `{CMD_HANDLER}help <modul>` untuk detail."
    )
    await message.edit(text[:4096])
