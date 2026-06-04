"""
Module: weather
Commands: .weather [city]
"""

import aiohttp
from pyrogram.types import Message

import eleger
from eleger import CMD_HANDLER
from eleger.helpers.decorator import eleger_cmd
from eleger.helpers.utils import edel

MODULE = "weather"
HELP = f"""
**Plugin:** `{MODULE}`

• `{CMD_HANDLER}weather <kota>` — Info cuaca terkini (wttr.in)
"""
eleger.CMD_HELP[MODULE] = HELP

_WEATHER_EMOJI = {
    "sunny": "☀️", "clear": "🌙", "cloudy": "☁️", "overcast": "🌥",
    "rain": "🌧", "drizzle": "🌦", "thunder": "⛈", "snow": "❄️",
    "fog": "🌫", "mist": "🌫", "blizzard": "🌨", "sleet": "🌨",
    "wind": "💨", "storm": "🌪",
}


def _weather_icon(desc: str) -> str:
    desc_lower = desc.lower()
    for k, v in _WEATHER_EMOJI.items():
        if k in desc_lower:
            return v
    return "🌡"


@eleger_cmd(r"weather (.+)")
async def weather_cmd(client, message: Message):
    """Get weather info from wttr.in."""
    city = message.matches[0].group(1).strip()
    await message.edit(f"`⏳ Mengambil cuaca untuk {city}...`")

    url = f"https://wttr.in/{aiohttp.helpers.requote_uri(city)}?format=j1"
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return await message.edit(f"❌ Kota `{city}` tidak ditemukan.")
                data = await resp.json(content_type=None)

        curr = data["current_condition"][0]
        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        desc = curr["weatherDesc"][0]["value"]
        temp_c = curr["temp_C"]
        temp_f = curr["temp_F"]
        feels_c = curr["FeelsLikeC"]
        humidity = curr["humidity"]
        wind_kmph = curr["windspeedKmph"]
        wind_dir = curr["winddir16Point"]
        visibility = curr["visibility"]
        pressure = curr["pressure"]
        uv = curr.get("uvIndex", "–")

        icon = _weather_icon(desc)
        text = (
            f"{icon} **Cuaca di {city_name}, {country}**\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🌤 **Kondisi:** `{desc}`\n"
            f"🌡 **Suhu:** `{temp_c}°C / {temp_f}°F`\n"
            f"🤔 **Terasa:** `{feels_c}°C`\n"
            f"💧 **Kelembapan:** `{humidity}%`\n"
            f"💨 **Angin:** `{wind_kmph} km/h {wind_dir}`\n"
            f"👁 **Visibilitas:** `{visibility} km`\n"
            f"📊 **Tekanan:** `{pressure} hPa`\n"
            f"☀️ **UV Index:** `{uv}`"
        )
        await message.edit(text)
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
