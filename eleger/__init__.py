"""
ElegerUbot — Pyrogram Userbot
Core initialization: config, logger, and client registry.
"""

import logging
import os
import sys
import time
from pathlib import Path

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# ─── Load environment ────────────────────────────────────────────────────────
_env_file = Path(__file__).parent.parent / "config.env"
if _env_file.exists():
    load_dotenv(_env_file)

# ─── Logger ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.ERROR)

LOGS = logging.getLogger("eleger")

# ─── Python version guard ─────────────────────────────────────────────────────
if sys.version_info < (3, 9):
    LOGS.critical("Python 3.9+ required. Bot stopped.")
    sys.exit(1)

# ─── Core Config ──────────────────────────────────────────────────────────────
API_ID: int = int(os.environ.get("API_ID") or 0)
API_HASH: str = os.environ.get("API_HASH") or ""
BOT_TOKEN: str = os.environ.get("BOT_TOKEN") or ""

if not API_ID or not API_HASH:
    LOGS.critical("API_ID and API_HASH are required. Set them in config.env or Railway variables.")
    sys.exit(1)

# ─── Session strings (up to 20 clients) ───────────────────────────────────────
SESSION_STRINGS: list[str] = []
for i in range(1, 21):
    key = f"STRING_SESSION_{i}"
    val = os.environ.get(key, "").strip()
    if not val and i == 1:
        val = os.environ.get("STRING_SESSION", "").strip()
    if val:
        SESSION_STRINGS.append(val)

if not SESSION_STRINGS:
    LOGS.critical(
        "No session string found! Set STRING_SESSION (or STRING_SESSION_1 … STRING_SESSION_20) in config."
    )
    sys.exit(1)

# ─── Bot settings ─────────────────────────────────────────────────────────────
CMD_HANDLER: str = os.environ.get("CMD_HANDLER", ".").strip() or "."
SUDO_HANDLER: str = os.environ.get("SUDO_HANDLER", "!").strip() or "!"

OWNER_ID: int = int(os.environ.get("OWNER_ID") or 0)
SUDO_USERS: set[int] = {
    int(x) for x in os.environ.get("SUDO_USERS", "").split() if x.isdigit()
}

LOG_CHAT: int = int(os.environ.get("LOG_CHAT") or 0)

BOT_VERSION: str = "1.0.0"
BOT_NAME: str = os.environ.get("BOT_NAME", "ElegerUbot")
ALIVE_MSG: str = os.environ.get(
    "ALIVE_MSG", f"⚡ **{BOT_NAME}** is alive and running!"
)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DATA_DIR = BASE_DIR / "data"

DOWNLOADS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# ─── Runtime state (populated after clients start) ────────────────────────────
CLIENTS: list = []          # List[ElegerClient]
ASSISTANT = None            # Assistant Pyrogram Client
START_TIME: float = time.time()

# ─── Module registry ──────────────────────────────────────────────────────────
CMD_HELP: dict[str, str] = {}     # module_name → help text
LOADED_MODULES: list[str] = []
