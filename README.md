# ElegerUbot

ElegerUbot adalah Telegram Userbot berbasis [Pyrogram](https://docs.pyrogram.org/) dengan desain modular dan dukungan **multi-client hingga 20 akun**. Proyek ini dibuat seringan dan semminimalis mungkin namun memiliki modul yang cukup lengkap, dan siap untuk di-deploy ke Railway.

## Fitur Utama
- **Berbasis Pyrogram** yang cepat dan efisien.
- **Multi-Client Support**: Dapat menjalankan hingga 20 akun dalam satu proses server, menghemat resource.
- **Arsitektur Modular**: Mudah menambah atau memodifikasi plugin di folder `modules/`.
- **Dynamic Helper Decorator**: Modul mendaftarkan handler yang secara otomatis disebar ke semua client aktif.

## Deploy ke Railway

### 1. Dapatkan Session String
Jalankan file generator di komputermu (butuh Python):
```bash
pip install pyrogram tgcrypto
python session_generator.py
```
Masukkan API ID dan API Hash dari [my.telegram.org](https://my.telegram.org). Kamu akan mendapatkan string session panjang.

### 2. Konfigurasi Railway
Buat project baru di Railway, sambungkan ke repository ini.
Di bagian **Variables**, tambahkan:

| Variable | Keterangan |
|----------|------------|
| `API_ID` | API ID dari Telegram |
| `API_HASH` | API Hash dari Telegram |
| `STRING_SESSION_1` | Session string dari generator |
| `STRING_SESSION_2` | (Opsional) Session client ke-2 |
| `...` | (Opsional) Sampai STRING_SESSION_20 |
| `CMD_HANDLER` | Prefix command (contoh: `.`) |
| `OWNER_ID` | ID akun utamamu |

## Menjalankan secara Lokal

1. Clone repositori ini.
2. Buat file `config.env` dengan format mengacu pada `.env.example`.
3. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan bot:
   ```bash
   python -m eleger
   ```

## Struktur Direktori

- `eleger/` — Core engine, modul loader, dan client manager.
- `eleger/helpers/` — Custom decorators (`@eleger_cmd`), utilities, dan filters.
- `modules/` — Folder tempat semua plugin/modul diletakkan (terbagi dalam `core`, `tools`, `admin`, `fun`, `utility`).

## Daftar Modul
Bot mencakup berbagai modul bawaan seperti:
- `.alive`, `.ping`, `.eval`
- `.info`, `.profile`, `.notes`, `.afk`, `.purge`
- `.ban`, `.kick`, `.mute`, `.promote`
- `.misc` (tts, tr, quote), `.media` (dl, upload)
- `.weather`, `.whois`, `.paste`, `.sangmata`
- `.gcast` (broadcast), `.clients` (cek status multi-client)
