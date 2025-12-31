#!/usr/bin/env python3
"""
Fetch historical context for a specific date to inject entropy into poster generation.

Creates a "reality palette" - temporal context that grounds each day in reality:
- Crypto market snapshot (BTC, ETH prices, sentiment)
- Weather in major tech hubs
- Top tech/world news headlines

Usage:
  # Fetch context for a date
  python scripts/posters/utils/reality_context.py 2025-12-21

  # Generate visual palette
  python scripts/posters/utils/reality_context.py 2025-12-21 -o palette.png

  # Output as JSON
  python scripts/posters/utils/reality_context.py 2025-12-21 --json

  # Get context for today
  python scripts/posters/utils/reality_context.py today
"""

import argparse
import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFont

# API endpoints
COINGECKO_HISTORY = "https://api.coingecko.com/api/v3/coins/{coin}/history"
FEAR_GREED_API = "https://api.alternative.me/fng/"
WTTR_API = "https://wttr.in/{city}?format=j1"
HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

# Cities for weather (major tech hubs)
WEATHER_CITIES = ["San+Francisco", "New+York", "London", "Singapore", "Tokyo"]

# Visual palette settings
PALETTE_WIDTH = 600
PALETTE_HEIGHT = 400
BG_COLOR = (25, 25, 35)  # Dark blue-gray
TEXT_COLOR = (220, 220, 230)
ACCENT_GREEN = (100, 200, 120)
ACCENT_RED = (220, 100, 100)
ACCENT_BLUE = (100, 150, 220)


# =============================================================================
# Crypto Data (CoinGecko)
# =============================================================================

def fetch_crypto_snapshot(date_str: str) -> dict:
    """Fetch BTC and ETH prices for a specific date.

    CoinGecko history API uses dd-mm-yyyy format.
    Returns current data if date is today.
    """
    try:
        # Parse date
        date = datetime.strptime(date_str, "%Y-%m-%d")
        cg_date = date.strftime("%d-%m-%Y")
        is_today = date.date() == datetime.now().date()

        coins = {}
        for coin in ["bitcoin", "ethereum"]:
            try:
                if is_today:
                    # Use simple price endpoint for today
                    resp = requests.get(
                        f"https://api.coingecko.com/api/v3/simple/price",
                        params={"ids": coin, "vs_currencies": "usd", "include_24hr_change": "true"},
                        timeout=10
                    )
                    if resp.ok:
                        data = resp.json().get(coin, {})
                        coins[coin] = {
                            "price": data.get("usd", 0),
                            "change_24h": data.get("usd_24h_change", 0),
                        }
                else:
                    # Historical data
                    resp = requests.get(
                        COINGECKO_HISTORY.format(coin=coin),
                        params={"date": cg_date, "localization": "false"},
                        timeout=10
                    )
                    if resp.ok:
                        data = resp.json()
                        market = data.get("market_data", {})
                        coins[coin] = {
                            "price": market.get("current_price", {}).get("usd", 0),
                            "change_24h": market.get("price_change_percentage_24h", 0),
                        }
            except Exception as e:
                coins[coin] = {"price": 0, "change_24h": 0, "error": str(e)}

        return {
            "btc": coins.get("bitcoin", {}),
            "eth": coins.get("ethereum", {}),
            "date": date_str,
        }
    except Exception as e:
        return {"error": str(e), "date": date_str}


def fetch_fear_greed(date_str: str = None) -> dict:
    """Fetch crypto Fear & Greed Index.

    Note: Historical data requires limit parameter.
    """
    try:
        # Calculate days ago for historical
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            days_ago = (datetime.now() - date).days
            limit = max(1, min(days_ago + 1, 365))  # API limit
        else:
            limit = 1

        resp = requests.get(
            FEAR_GREED_API,
            params={"limit": limit, "format": "json"},
            timeout=10
        )

        if resp.ok:
            data = resp.json().get("data", [])
            if data:
                # Find closest date
                if date_str:
                    target_ts = datetime.strptime(date_str, "%Y-%m-%d").timestamp()
                    closest = min(data, key=lambda x: abs(int(x.get("timestamp", 0)) - target_ts))
                else:
                    closest = data[0]

                return {
                    "value": int(closest.get("value", 50)),
                    "classification": closest.get("value_classification", "Neutral"),
                }

        return {"value": 50, "classification": "Neutral"}
    except Exception as e:
        return {"value": 50, "classification": "Neutral", "error": str(e)}


# =============================================================================
# Weather (wttr.in)
# =============================================================================

def fetch_weather_snapshot(date_str: str = None) -> dict:
    """Fetch current weather for major tech hubs.

    Note: wttr.in doesn't support historical data easily,
    so we fetch current weather (useful for "today" context).
    For historical, we'd need a paid service.
    """
    weather = {}

    for city in WEATHER_CITIES[:3]:  # Limit to 3 to avoid rate limiting
        try:
            resp = requests.get(
                WTTR_API.format(city=city),
                timeout=10
            )
            if resp.ok:
                data = resp.json()
                current = data.get("current_condition", [{}])[0]

                city_name = city.replace("+", " ")
                weather[city_name] = {
                    "temp_f": int(current.get("temp_F", 0)),
                    "temp_c": int(current.get("temp_C", 0)),
                    "condition": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                    "humidity": int(current.get("humidity", 0)),
                }
        except Exception:
            continue

    return weather


def get_weather_emoji(condition: str) -> str:
    """Convert weather condition to emoji."""
    condition = condition.lower()
    if "sun" in condition or "clear" in condition:
        return "☀️"
    elif "cloud" in condition and "part" in condition:
        return "⛅"
    elif "cloud" in condition or "overcast" in condition:
        return "☁️"
    elif "rain" in condition or "drizzle" in condition:
        return "🌧️"
    elif "snow" in condition:
        return "❄️"
    elif "thunder" in condition or "storm" in condition:
        return "⛈️"
    elif "fog" in condition or "mist" in condition:
        return "🌫️"
    else:
        return "🌤️"


# =============================================================================
# News (Hacker News)
# =============================================================================

def fetch_hn_top_stories(limit: int = 5) -> list:
    """Fetch top Hacker News stories.

    Note: HN API doesn't support historical easily.
    For historical, we'd use hn.algolia.com/api.
    """
    try:
        resp = requests.get(HN_TOP_STORIES, timeout=10)
        if not resp.ok:
            return []

        story_ids = resp.json()[:limit]
        stories = []

        for sid in story_ids:
            try:
                item_resp = requests.get(HN_ITEM.format(id=sid), timeout=5)
                if item_resp.ok:
                    item = item_resp.json()
                    stories.append({
                        "title": item.get("title", ""),
                        "score": item.get("score", 0),
                        "url": item.get("url", ""),
                    })
            except Exception:
                continue

        return stories
    except Exception:
        return []


def fetch_hn_historical(date_str: str, limit: int = 5) -> list:
    """Fetch historical HN stories using Algolia API."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        # Search for stories from that date
        start_ts = int(date.timestamp())
        end_ts = int((date + timedelta(days=1)).timestamp())

        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "tags": "story",
                "numericFilters": f"created_at_i>={start_ts},created_at_i<{end_ts}",
                "hitsPerPage": limit,
            },
            timeout=10
        )

        if resp.ok:
            hits = resp.json().get("hits", [])
            return [
                {
                    "title": h.get("title", ""),
                    "score": h.get("points", 0),
                    "url": h.get("url", ""),
                }
                for h in hits
            ]
        return []
    except Exception:
        return []


# =============================================================================
# Combined Context
# =============================================================================

def fetch_reality_context(date_str: str) -> dict:
    """Fetch all reality context for a date.

    Returns combined context from all sources.
    """
    # Normalize date
    if date_str.lower() == "today":
        date_str = datetime.now().strftime("%Y-%m-%d")

    is_today = date_str == datetime.now().strftime("%Y-%m-%d")

    # Fetch all data
    crypto = fetch_crypto_snapshot(date_str)
    sentiment = fetch_fear_greed(date_str)
    weather = fetch_weather_snapshot() if is_today else {}

    # News - use historical API for past dates
    if is_today:
        news = fetch_hn_top_stories(5)
    else:
        news = fetch_hn_historical(date_str, 5)

    # Derive mood
    mood = derive_mood(crypto, sentiment, weather, news)

    return {
        "date": date_str,
        "crypto": crypto,
        "sentiment": sentiment,
        "weather": weather,
        "news": news,
        "mood": mood,
    }


def derive_mood(crypto: dict, sentiment: dict, weather: dict, news: list) -> dict:
    """Derive overall mood/vibe from context."""
    # Market mood
    btc_change = crypto.get("btc", {}).get("change_24h", 0)
    if btc_change > 5:
        market_mood = "euphoric"
    elif btc_change > 2:
        market_mood = "bullish"
    elif btc_change > 0:
        market_mood = "optimistic"
    elif btc_change > -2:
        market_mood = "cautious"
    elif btc_change > -5:
        market_mood = "bearish"
    else:
        market_mood = "fearful"

    # Fear/greed classification
    fg_value = sentiment.get("value", 50)
    if fg_value >= 75:
        sentiment_mood = "extreme greed"
    elif fg_value >= 55:
        sentiment_mood = "greed"
    elif fg_value >= 45:
        sentiment_mood = "neutral"
    elif fg_value >= 25:
        sentiment_mood = "fear"
    else:
        sentiment_mood = "extreme fear"

    # Weather-based atmosphere (if available)
    atmosphere = "neutral"
    if weather:
        temps = [w.get("temp_f", 70) for w in weather.values()]
        avg_temp = sum(temps) / len(temps) if temps else 70
        if avg_temp > 85:
            atmosphere = "hot summer"
        elif avg_temp > 70:
            atmosphere = "warm"
        elif avg_temp > 50:
            atmosphere = "mild"
        elif avg_temp > 32:
            atmosphere = "cold"
        else:
            atmosphere = "freezing winter"

    # Combine into summary
    btc_price = crypto.get("btc", {}).get("price", 0)
    price_str = f"${btc_price:,.0f}" if btc_price else "unknown"

    return {
        "market": market_mood,
        "sentiment": sentiment_mood,
        "atmosphere": atmosphere,
        "summary": f"BTC at {price_str}, {market_mood} market, {sentiment_mood} sentiment, {atmosphere} vibes",
    }


# =============================================================================
# Visual Palette Generation
# =============================================================================

def make_reality_palette(context: dict) -> bytes:
    """Create visual reality palette PNG from context."""
    img = Image.new("RGB", (PALETTE_WIDTH, PALETTE_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # Header
    date_str = context.get("date", "Unknown")
    draw.text((20, 15), "REALITY PALETTE", fill=TEXT_COLOR, font=font_large)
    draw.text((PALETTE_WIDTH - 120, 20), date_str, fill=ACCENT_BLUE, font=font_medium)

    # Divider
    draw.line([(20, 50), (PALETTE_WIDTH - 20, 50)], fill=(60, 60, 70), width=2)

    # === CRYPTO SECTION ===
    y = 70
    draw.text((20, y), "CRYPTO", fill=ACCENT_BLUE, font=font_medium)

    crypto = context.get("crypto", {})
    btc = crypto.get("btc", {})
    eth = crypto.get("eth", {})

    btc_price = btc.get("price", 0)
    btc_change = btc.get("change_24h", 0)
    eth_price = eth.get("price", 0)
    eth_change = eth.get("change_24h", 0)

    y += 30
    btc_color = ACCENT_GREEN if btc_change >= 0 else ACCENT_RED
    change_symbol = "+" if btc_change >= 0 else ""
    draw.text((30, y), f"BTC: ${btc_price:,.0f}", fill=TEXT_COLOR, font=font_medium)
    draw.text((180, y), f"{change_symbol}{btc_change:.1f}%", fill=btc_color, font=font_medium)

    y += 25
    eth_color = ACCENT_GREEN if eth_change >= 0 else ACCENT_RED
    change_symbol = "+" if eth_change >= 0 else ""
    draw.text((30, y), f"ETH: ${eth_price:,.0f}", fill=TEXT_COLOR, font=font_medium)
    draw.text((180, y), f"{change_symbol}{eth_change:.1f}%", fill=eth_color, font=font_medium)

    # Fear/Greed
    sentiment = context.get("sentiment", {})
    fg_value = sentiment.get("value", 50)
    fg_class = sentiment.get("classification", "Neutral")

    y += 30
    fg_color = ACCENT_GREEN if fg_value > 50 else ACCENT_RED if fg_value < 50 else TEXT_COLOR
    draw.text((30, y), f"Fear/Greed: {fg_value}", fill=fg_color, font=font_medium)
    draw.text((180, y), fg_class, fill=fg_color, font=font_small)

    # === WEATHER SECTION ===
    weather = context.get("weather", {})
    if weather:
        y = 70
        draw.text((300, y), "WEATHER", fill=ACCENT_BLUE, font=font_medium)

        y += 30
        for city, data in list(weather.items())[:3]:
            emoji = get_weather_emoji(data.get("condition", ""))
            temp = data.get("temp_f", 0)
            draw.text((310, y), f"{emoji} {city}: {temp}°F", fill=TEXT_COLOR, font=font_small)
            y += 20

    # === NEWS SECTION ===
    y = 200
    draw.line([(20, y - 10), (PALETTE_WIDTH - 20, y - 10)], fill=(60, 60, 70), width=1)
    draw.text((20, y), "TOP STORIES", fill=ACCENT_BLUE, font=font_medium)

    news = context.get("news", [])
    y += 30
    for story in news[:4]:
        title = story.get("title", "")[:70]
        if len(story.get("title", "")) > 70:
            title += "..."
        draw.text((30, y), f"• {title}", fill=TEXT_COLOR, font=font_small)
        y += 22

    # === MOOD SUMMARY ===
    mood = context.get("mood", {})
    summary = mood.get("summary", "")

    y = PALETTE_HEIGHT - 50
    draw.line([(20, y - 10), (PALETTE_WIDTH - 20, y - 10)], fill=(60, 60, 70), width=1)
    draw.text((20, y), "MOOD:", fill=ACCENT_BLUE, font=font_medium)
    draw.text((80, y), summary[:80], fill=TEXT_COLOR, font=font_small)

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def context_to_prompt(context: dict) -> str:
    """Convert context to prompt injection text."""
    date = context.get("date", "unknown")
    crypto = context.get("crypto", {})
    sentiment = context.get("sentiment", {})
    mood = context.get("mood", {})
    news = context.get("news", [])

    btc_price = crypto.get("btc", {}).get("price", 0)
    btc_change = crypto.get("btc", {}).get("change_24h", 0)
    fg_value = sentiment.get("value", 50)
    fg_class = sentiment.get("classification", "Neutral")

    # Top headline
    top_headline = news[0].get("title", "") if news else "No headlines"

    change_word = "up" if btc_change >= 0 else "down"

    return (
        f"Historical context for {date}: "
        f"Bitcoin at ${btc_price:,.0f} ({change_word} {abs(btc_change):.1f}%), "
        f"market sentiment is {fg_class.lower()} (Fear/Greed: {fg_value}). "
        f"Top tech headline: \"{top_headline[:60]}\". "
        f"Overall mood: {mood.get('market', 'neutral')}. "
        f"Reflect this temporal context in the visual atmosphere."
    )


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fetch historical context for poster generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "date",
        help="Date in YYYY-MM-DD format, or 'today'"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output path for visual palette PNG"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output context as JSON"
    )
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Output as prompt injection text"
    )

    args = parser.parse_args()

    # Normalize date
    if args.date.lower() == "today":
        date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = args.date

    print(f"Fetching reality context for {date_str}...", file=sys.stderr)

    context = fetch_reality_context(date_str)

    if args.json:
        print(json.dumps(context, indent=2))
    elif args.prompt:
        print(context_to_prompt(context))
    elif args.output:
        palette_bytes = make_reality_palette(context)
        args.output.write_bytes(palette_bytes)
        print(f"Saved: {args.output}", file=sys.stderr)
    else:
        # Default: print summary
        print(f"\n=== Reality Context: {date_str} ===\n")

        crypto = context.get("crypto", {})
        btc = crypto.get("btc", {})
        eth = crypto.get("eth", {})
        print(f"CRYPTO:")
        print(f"  BTC: ${btc.get('price', 0):,.0f} ({btc.get('change_24h', 0):+.1f}%)")
        print(f"  ETH: ${eth.get('price', 0):,.0f} ({eth.get('change_24h', 0):+.1f}%)")

        sentiment = context.get("sentiment", {})
        print(f"  Fear/Greed: {sentiment.get('value', 50)} ({sentiment.get('classification', 'Neutral')})")

        weather = context.get("weather", {})
        if weather:
            print(f"\nWEATHER:")
            for city, data in weather.items():
                emoji = get_weather_emoji(data.get("condition", ""))
                print(f"  {city}: {data.get('temp_f', 0)}°F {emoji} {data.get('condition', '')}")

        news = context.get("news", [])
        if news:
            print(f"\nTOP STORIES:")
            for story in news[:5]:
                print(f"  • {story.get('title', '')[:70]}")

        mood = context.get("mood", {})
        print(f"\nMOOD: {mood.get('summary', '')}")


if __name__ == "__main__":
    main()
