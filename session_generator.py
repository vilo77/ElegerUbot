import asyncio
from pyrogram import Client

print("=== ElegerUbot Session Generator ===")
print("Pastikan kamu sudah memiliki API_ID dan API_HASH dari my.telegram.org")
print("=====================================\n")

API_ID = input("Masukkan API_ID: ")
API_HASH = input("Masukkan API_HASH: ")

async def generate():
    async with Client(
        "generator",
        api_id=int(API_ID),
        api_hash=API_HASH,
        in_memory=True
    ) as app:
        session_string = await app.export_session_string()
        print("\n✅ BERHASIL!")
        print("Ini adalah STRING_SESSION kamu (jangan berikan ke siapa-siapa):")
        print(f"\n`{session_string}`\n")
        print("Simpan string ini di variabel environment STRING_SESSION_1 di Railway.")

if __name__ == "__main__":
    asyncio.run(generate())
