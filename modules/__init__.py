"""
Modules package — auto-discovered by eleger/loader.py
"""
import logging

# Inisialisasi Logger agar tidak error lagi
logger = logging.getLogger("eleger")

# Variabel Global untuk Assistant Bot
assistant = None

# Konfigurasi level logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
