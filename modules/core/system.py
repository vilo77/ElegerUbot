"""
Module: system
Commands: .stats, .sysinfo, .restart
"""

import os
import sys
import time
import platform

from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER, BOT_NAME, BOT_VERSION, START_TIME
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import uptime_str, human_size

MODULE = "system"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}stats` — Statistik proses & memori
• `{CMD_HANDLER}sysinfo` — Info sistem (OS, CPU, RAM)
• `{CMD_HANDLER}restart` — Restart semua client (Railway auto-restart)
"""
eleger.CMD_HELP[MODULE] = HELP


@eleger_cmd(r"stats$")
async def stats_cmd(client, message: Message):
    """Show process and module stats."""
    uptime = uptime_str(START_TIME)
    total_clients = len(eleger.CLIENTS)
    total_modules = len(eleger.LOADED_MODULES)
    total_cmds = sum(1 for _ in eleger.CMD_HELP)

    try:
        import psutil
        proc = psutil.Process(os.getpid())
        mem = proc.memory_info()
        rss = human_size(mem.rss)
        vms = human_size(mem.vms)
        cpu = f"{proc.cpu_percent(interval=0.1):.1f}%"
    except ImportError:
        rss = vms = cpu = "N/A (psutil not installed)"

    text = (
        f"📊 **{BOT_NAME} Stats**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"👥 **Clients:** `{total_clients}`\n"
        f"📦 **Modules:** `{total_modules}`\n"
        f"📌 **Prefix:** `{eleger.CMD_HANDLER}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💾 **RAM (RSS):** `{rss}`\n"
        f"💽 **RAM (VMS):** `{vms}`\n"
        f"⚙️ **CPU:** `{cpu}`\n"
        f"🐍 **Python:** `{sys.version.split()[0]}`\n"
        f"🤖 **Version:** `{BOT_VERSION}`"
    )
    await message.edit(text)


@eleger_cmd(r"sysinfo$")
async def sysinfo_cmd(client, message: Message):
    """Show system information."""
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        boot_time = uptime_str(psutil.boot_time())
        ram_total = human_size(mem.total)
        ram_used = human_size(mem.used)
        ram_pct = f"{mem.percent}%"
        disk_total = human_size(disk.total)
        disk_used = human_size(disk.used)
        disk_pct = f"{disk.percent}%"
    except ImportError:
        cpu_count = cpu_freq_str = ram_total = ram_used = ram_pct = "N/A"
        disk_total = disk_used = disk_pct = boot_time = "N/A"

    text = (
        f"🖥 **System Info**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🖥 **OS:** `{platform.system()} {platform.release()}`\n"
        f"🏗 **Arch:** `{platform.machine()}`\n"
        f"⚙️ **CPU Cores:** `{cpu_count}`\n"
        f"📡 **CPU Freq:** `{cpu_freq_str}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🧠 **RAM Total:** `{ram_total}`\n"
        f"🧠 **RAM Used:** `{ram_used}` ({ram_pct})\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💿 **Disk Total:** `{disk_total}`\n"
        f"💿 **Disk Used:** `{disk_used}` ({disk_pct})\n"
        f"⏱ **System Uptime:** `{boot_time}`"
    )
    await message.edit(text)


@eleger_cmd(r"restart$", allow_sudo=False)
async def restart_cmd(client, message: Message):
    """Restart the userbot (Railway will auto-restart the process)."""
    await message.edit("🔄 **Restarting ElegerUbot...**")
    os.execv(sys.executable, [sys.executable, "-m", "eleger"])
