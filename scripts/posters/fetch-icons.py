#!/usr/bin/env python3
"""
Fetch token icons from CoinGecko API.
Rate limited: 3s between requests (free tier: ~10-30/min)

Usage:
  python scripts/posters/fetch-icons.py --tokens      # Fetch mapped tokens only (fast)
  python scripts/posters/fetch-icons.py --discover    # Try ALL inventory tokens on CoinGecko (slow)
  python scripts/posters/fetch-icons.py --token eth   # Fetch specific token
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Optional
import requests

SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
ENTITY_INVENTORY = ASSETS_DIR / "entity-inventory.json"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# CoinGecko ID mappings for common tokens
# Maps normalized entity name -> CoinGecko coin ID
COINGECKO_IDS = {
    # Major tokens
    "bitcoin": "bitcoin",
    "btc": "bitcoin",
    "ethereum": "ethereum",
    "eth": "ethereum",
    "solana": "solana",
    "sol": "solana",
    "usdc": "usd-coin",
    "usdt": "tether",
    "weth": "weth",
    "wbtc": "wrapped-bitcoin",
    "bonk": "bonk",
    "dogwifhat": "dogwifcoin",

    # Ecosystem tokens
    "ai16z": "ai16z",
    "virtual": "virtual-protocol",
    "worldcoin": "worldcoin-wld",
    "dot": "polkadot",
    "icp": "internet-computer",
    "bnb": "binancecoin",
    "avax": "avalanche-2",
    "matic": "matic-network",
    "polygon": "matic-network",
    "xmr": "monero",
    "monero": "monero",
    "eliza": "eliza",
    "wld": "worldcoin-wld",
}



def fetch_coingecko_icon(coin_id: str, output_path: Path) -> bool:
    """Fetch token icon from CoinGecko API."""
    if output_path.exists():
        logging.info(f"  [skip] {coin_id} - already exists")
        return True

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Get the large image URL
        image_url = data.get("image", {}).get("large")
        if not image_url:
            logging.warning(f"  [warn] {coin_id} - no image found")
            return False

        # Download the image
        img_response = requests.get(image_url, timeout=10)
        img_response.raise_for_status()

        output_path.write_bytes(img_response.content)
        logging.info(f"  [ok] {coin_id} -> {output_path.name}")
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.warning(f"  [404] {coin_id} - not found on CoinGecko")
        else:
            logging.error(f"  [error] {coin_id} - {e}")
        return False
    except Exception as e:
        logging.error(f"  [error] {coin_id} - {e}")
        return False


COINGECKO_RATE_LIMIT = 3  # seconds between requests (free tier: ~10-30/min)


def get_existing_icons(directory: Path) -> set:
    """Get set of existing icon basenames (without extension)."""
    if not directory.exists():
        return set()
    return {f.stem.lower() for f in directory.iterdir() if f.is_file()}


def fetch_tokens(specific: str = None, discover: bool = False):
    """Fetch token icons from CoinGecko."""
    tokens_dir = ICONS_DIR / "tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    if specific:
        # Fetch specific token
        coin_id = COINGECKO_IDS.get(specific.lower(), specific.lower())
        output = tokens_dir / f"{specific.lower()}.png"
        if output.exists():
            logging.info(f"Already have {specific}")
            return
        logging.info(f"Fetching {specific} from CoinGecko...")
        fetch_coingecko_icon(coin_id, output)
        return

    # Pre-scan existing icons
    existing = get_existing_icons(tokens_dir)
    logging.info(f"Found {len(existing)} existing token icons")

    if discover and ENTITY_INVENTORY.exists():
        # Try to fetch all tokens from inventory
        with open(ENTITY_INVENTORY) as f:
            inventory = json.load(f)
        tokens = inventory.get("entities", {}).get("tokens", [])

        # Filter to only missing tokens
        to_fetch = []
        for token in tokens:
            name = token.lower().strip().lstrip('$')
            if len(name) >= 2 and name not in existing:
                coin_id = COINGECKO_IDS.get(name, name)
                to_fetch.append((name, coin_id))

        logging.info(f"Need to fetch {len(to_fetch)} tokens ({len(tokens) - len(to_fetch)} already exist)")

        if not to_fetch:
            return

        success, failed = 0, 0
        for i, (name, coin_id) in enumerate(to_fetch):
            output = tokens_dir / f"{name}.png"
            logging.info(f"  [{i+1}/{len(to_fetch)}] {name} ({coin_id})...")
            if fetch_coingecko_icon(coin_id, output):
                success += 1
            else:
                failed += 1
            if i < len(to_fetch) - 1:  # Don't sleep after last request
                time.sleep(COINGECKO_RATE_LIMIT)

        logging.info(f"Done: {success} fetched, {failed} not found")
    else:
        # Fetch mapped tokens only
        to_fetch = [(name, cid) for name, cid in COINGECKO_IDS.items() if name not in existing]

        logging.info(f"Need to fetch {len(to_fetch)} tokens ({len(COINGECKO_IDS) - len(to_fetch)} already exist)")

        if not to_fetch:
            return

        success = 0
        for i, (entity_name, coin_id) in enumerate(to_fetch):
            output = tokens_dir / f"{entity_name}.png"
            if fetch_coingecko_icon(coin_id, output):
                success += 1
            if i < len(to_fetch) - 1:
                time.sleep(COINGECKO_RATE_LIMIT)

        logging.info(f"Fetched {success}/{len(to_fetch)} token icons")


def main():
    parser = argparse.ArgumentParser(description="Fetch token icons from CoinGecko")
    parser.add_argument("--tokens", action="store_true", help="Fetch all mapped token icons")
    parser.add_argument("--discover", action="store_true", help="Try ALL inventory tokens on CoinGecko (slow)")
    parser.add_argument("--token", type=str, help="Fetch specific token by name")
    args = parser.parse_args()

    if args.token:
        fetch_tokens(args.token)
    elif args.discover:
        fetch_tokens(discover=True)
    elif args.tokens:
        fetch_tokens()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
