"""
Module: eval
Commands: .eval, .exec, .sh
"""

import asyncio
import io
import os
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edit

MODULE = "eval"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}eval <expr>` — Evaluasi ekspresi Python
• `{CMD_HANDLER}exec <code>` — Jalankan kode Python multi-baris
• `{CMD_HANDLER}sh <cmd>` — Jalankan perintah shell
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"eval (.+)", allow_sudo=False)
async def eval_cmd(client, message: Message):
    """Evaluate a Python expression."""
    code = message.matches[0].group(1).strip()
    await message.edit(f"`⏳ Evaluating...`")
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    result = None
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            result = eval(code, {"client": client, "message": message, "eleger": eleger})  # noqa: S307
        out = stdout_buf.getvalue()
        err = stderr_buf.getvalue()
        text = f"**📥 Input:**\n`{code}`\n\n**📤 Output:**\n`{result}`"
        if out:
            text += f"\n\n**stdout:**\n`{out.strip()}`"
        if err:
            text += f"\n\n**stderr:**\n`{err.strip()}`"
    except Exception:
        tb = traceback.format_exc()
        text = f"**📥 Input:**\n`{code}`\n\n**❌ Error:**\n`{tb.strip()}`"
    await message.edit(text[:4096])


@eleger_cmd(r"exec (.+)", allow_sudo=False, disable_edited=False)
async def exec_cmd(client, message: Message):
    """Execute multi-line Python code."""
    code = message.matches[0].group(1).strip()
    # Support code blocks
    if code.startswith("```"):
        code = code.strip("`").lstrip("python").lstrip("\n")
    await message.edit("`⏳ Executing...`")

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    _locals = {"client": client, "message": message, "eleger": eleger}

    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(compile(code, "<exec>", "exec"), _locals)  # noqa: S102
        out = stdout_buf.getvalue() or "✅ Done (no output)"
        err = stderr_buf.getvalue()
        text = f"**📥 Code:**\n`{code[:200]}`\n\n**📤 Output:**\n`{out.strip()[:800]}`"
        if err:
            text += f"\n\n**stderr:**\n`{err.strip()[:400]}`"
    except Exception:
        tb = traceback.format_exc()
        text = f"**📥 Code:**\n`{code[:200]}`\n\n**❌ Error:**\n`{tb.strip()[:1000]}`"
    await message.edit(text[:4096])


@eleger_cmd(r"sh (.+)", allow_sudo=False)
async def shell_cmd(client, message: Message):
    """Run a shell command."""
    cmd = message.matches[0].group(1).strip()
    await message.edit(f"```\n$ {cmd}\n⏳ Running...\n```")
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        out = (stdout.decode() + stderr.decode()).strip() or "✅ (no output)"
    except asyncio.TimeoutError:
        out = "❌ Command timed out (30s)"
    except Exception as e:
        out = f"❌ Error: {e}"
    text = f"```\n$ {cmd}\n\n{out[:3500]}\n```"
    await message.edit(text)
