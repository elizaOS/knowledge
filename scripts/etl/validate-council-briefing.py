#!/usr/bin/env python3
"""Validate one or more council briefing files against the V2 consumer contract."""

import argparse
import json
import sys
from pathlib import Path

from council_schema import (
    CouncilValidationError,
    is_legacy_briefing,
    validate_consumer_contract,
    validate_council_briefing,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--allow-legacy",
        action="store_true",
        help="Skip valid pre-V2 briefings when scanning historical data",
    )
    parser.add_argument(
        "--consumer-only",
        action="store_true",
        help="Check fields dereferenced by consumers across mixed historical schemas",
    )
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        try:
            data = json.loads(path.read_text())
            if args.consumer_only:
                validate_consumer_contract(data)
                print(f"OK: {path}")
                continue
            if args.allow_legacy and is_legacy_briefing(data):
                print(f"SKIP legacy: {path}")
                continue
            expected_date = None if path.name == "daily.json" else path.stem
            validate_council_briefing(data, expected_date=expected_date)
            print(f"OK: {path}")
        except (OSError, json.JSONDecodeError, CouncilValidationError) as error:
            print(f"INVALID: {path}: {error}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
