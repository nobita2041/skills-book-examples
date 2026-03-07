from contextlib import asynccontextmanager

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
GEOCODING_BASE = "https://geocoding-api.open-meteo.com/v1"


@asynccontextmanager
async def lifespan(mcp: FastMCP):
    async with httpx.AsyncClient(timeout=30) as client:
        yield {"http_client": client}


mcp = FastMCP("Weather", lifespan=lifespan)


async def geocode(client: httpx.AsyncClient, city: str) -> dict:
    """都市名から緯度経度を取得する。"""
    resp = await client.get(
        f"{GEOCODING_BASE}/search",
        params={"name": city, "count": 1, "language": "ja"},
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("results"):
        raise ValueError(f"'{city}' が見つかりませんでした。正しい都市名を指定してください。")
    result = data["results"][0]
    return {
        "name": result.get("name", city),
        "country": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }


WMO_CODES = {
    0: "快晴", 1: "晴れ", 2: "一部曇り", 3: "曇り",
    45: "霧", 48: "着氷性の霧",
    51: "弱い霧雨", 53: "霧雨", 55: "強い霧雨",
    61: "弱い雨", 63: "雨", 65: "強い雨",
    71: "弱い雪", 73: "雪", 75: "強い雪",
    77: "霧雪",
    80: "弱いにわか雨", 81: "にわか雨", 82: "強いにわか雨",
    85: "弱いにわか雪", 86: "強いにわか雪",
    95: "雷雨", 96: "雹を伴う雷雨", 99: "激しい雹を伴う雷雨",
}


def weather_description(code: int) -> str:
    return WMO_CODES.get(code, f"不明({code})")


@mcp.tool
async def get_current_weather(city: str, ctx: Context) -> str:
    """指定した都市の現在の天気情報を取得します。

    Args:
        city: 都市名（例: 東京、大阪、New York）
    """
    client: httpx.AsyncClient = ctx.lifespan_context["http_client"]

    location = await geocode(client, city)

    resp = await client.get(
        f"{OPEN_METEO_BASE}/forecast",
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation",
            "timezone": "auto",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    current = data["current"]
    units = data["current_units"]

    return (
        f"## {location['name']}（{location['country']}）の現在の天気\n\n"
        f"- 天気: {weather_description(current['weather_code'])}\n"
        f"- 気温: {current['temperature_2m']}{units['temperature_2m']}\n"
        f"- 体感温度: {current['apparent_temperature']}{units['apparent_temperature']}\n"
        f"- 湿度: {current['relative_humidity_2m']}{units['relative_humidity_2m']}\n"
        f"- 風速: {current['wind_speed_10m']}{units['wind_speed_10m']}\n"
        f"- 風向: {current['wind_direction_10m']}{units['wind_direction_10m']}\n"
        f"- 降水量: {current['precipitation']}{units['precipitation']}\n"
    )


@mcp.tool
async def get_weekly_forecast(city: str, ctx: Context) -> str:
    """指定した都市の週間天気予報（7日間）を取得します。

    Args:
        city: 都市名（例: 東京、大阪、New York）
    """
    client: httpx.AsyncClient = ctx.lifespan_context["http_client"]

    location = await geocode(client, city)

    resp = await client.get(
        f"{OPEN_METEO_BASE}/forecast",
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "auto",
            "forecast_days": 7,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    daily = data["daily"]
    units = data["daily_units"]

    lines = [f"## {location['name']}（{location['country']}）の週間天気予報\n"]
    lines.append(
        f"| 日付 | 天気 | 最高気温 | 最低気温 | 降水確率 | 降水量 | 最大風速 |"
    )
    lines.append("|------|------|----------|----------|----------|--------|----------|")

    for i in range(len(daily["time"])):
        lines.append(
            f"| {daily['time'][i]} "
            f"| {weather_description(daily['weather_code'][i])} "
            f"| {daily['temperature_2m_max'][i]}{units['temperature_2m_max']} "
            f"| {daily['temperature_2m_min'][i]}{units['temperature_2m_min']} "
            f"| {daily['precipitation_probability_max'][i]}{units['precipitation_probability_max']} "
            f"| {daily['precipitation_sum'][i]}{units['precipitation_sum']} "
            f"| {daily['wind_speed_10m_max'][i]}{units['wind_speed_10m_max']} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
