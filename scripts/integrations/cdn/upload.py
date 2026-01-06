#!/usr/bin/env python3
"""
Upload files to Bunny CDN Storage.

Usage:
  # Upload a single file
  python scripts/integrations/cdn/upload.py posters/2025-12-21/overall.png

  # Upload entire directory
  python scripts/integrations/cdn/upload.py posters/2025-12-21/

  # Upload with custom remote path
  python scripts/integrations/cdn/upload.py local.png --remote posters/custom/image.png

  # Dry run (show what would be uploaded)
  python scripts/integrations/cdn/upload.py posters/2025-12-21/ --dry-run

  # Return URLs as JSON (for pipeline integration)
  python scripts/integrations/cdn/upload.py posters/2025-12-21/ --json

Environment Variables:
  BUNNY_STORAGE_ZONE     - Storage zone name (required)
  BUNNY_STORAGE_PASSWORD - Storage zone API password (required)
  BUNNY_CDN_URL          - CDN pull zone URL (default: https://{zone}.b-cdn.net)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, rely on environment variables
    pass

# --------------- Config ---------------

STORAGE_ZONE = os.environ.get("BUNNY_STORAGE_ZONE", "m3tv")
STORAGE_PASSWORD = os.environ.get("BUNNY_STORAGE_PASSWORD", "")
CDN_URL = os.environ.get("BUNNY_CDN_URL", "https://m3tv.b-cdn.net")

# Bunny Storage API endpoint (region-specific)
# Common regions: storage.bunnycdn.com, la.storage.bunnycdn.com, ny.storage.bunnycdn.com,
#                 sg.storage.bunnycdn.com, uk.storage.bunnycdn.com, etc.
STORAGE_API_BASE = os.environ.get("BUNNY_STORAGE_HOST", "https://la.storage.bunnycdn.com")

# File types to upload
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".json"}

# Max file size (10MB) - prevents accidental huge uploads
MAX_FILE_SIZE = 10 * 1024 * 1024


# --------------- Upload Functions ---------------


def get_cdn_url(storage_zone: str) -> str:
    """Get CDN URL, using env var or constructing default."""
    if CDN_URL:
        return CDN_URL.rstrip("/")
    return f"https://{storage_zone}.b-cdn.net"


def validate_remote_path(remote_path: str) -> tuple[bool, str]:
    """Validate remote path for security issues.

    Returns:
        (is_valid, sanitized_path_or_error)
    """
    # Strip leading slashes
    clean_path = remote_path.lstrip("/")

    # Block path traversal
    if ".." in clean_path:
        return False, "Path traversal not allowed"

    # Block suspicious patterns
    if any(c in clean_path for c in ["<", ">", "|", "\x00"]):
        return False, "Invalid characters in path"

    return True, clean_path


def upload_file(
    local_path: Path,
    remote_path: str,
    storage_zone: str,
    password: str,
) -> tuple[bool, str]:
    """Upload a single file to Bunny Storage.

    Args:
        local_path: Local file path
        remote_path: Remote path within storage zone (e.g., "posters/2025-12-21/overall.png")
        storage_zone: Bunny storage zone name
        password: Storage zone API password

    Returns:
        (success, message) tuple
    """
    # Validate remote path
    is_valid, result = validate_remote_path(remote_path)
    if not is_valid:
        return False, f"Invalid path: {result}"
    remote_path = result

    # Check file size
    file_size = local_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large: {file_size / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"

    url = f"{STORAGE_API_BASE}/{storage_zone}/{remote_path}"

    # Simple retry for transient errors
    last_error = None
    for attempt in range(2):
        try:
            with open(local_path, "rb") as f:
                response = requests.put(
                    url,
                    headers={
                        "AccessKey": password,
                        "Content-Type": "application/octet-stream",
                    },
                    data=f,
                    timeout=120,
                )

            if response.status_code in (200, 201):
                return True, "uploaded"
            elif response.status_code >= 500:
                # Server error - retry
                last_error = f"HTTP {response.status_code}"
                continue
            else:
                # Client error - don't retry
                return False, f"HTTP {response.status_code}: {response.text[:100]}"

        except requests.ConnectionError as e:
            last_error = f"Connection error: {e}"
            continue
        except requests.Timeout as e:
            last_error = f"Timeout: {e}"
            continue
        except requests.RequestException as e:
            return False, f"Request error: {e}"
        except IOError as e:
            return False, f"File error: {e}"

    return False, f"Failed after retry: {last_error}"


def upload_directory(
    local_dir: Path,
    remote_prefix: str,
    storage_zone: str,
    password: str,
    dry_run: bool = False,
) -> list[dict]:
    """Upload all files in a directory.

    Args:
        local_dir: Local directory path
        remote_prefix: Remote path prefix (e.g., "posters/2025-12-21")
        storage_zone: Bunny storage zone name
        password: Storage zone API password
        dry_run: If True, don't actually upload

    Returns:
        List of upload results with local_path, remote_path, cdn_url, success
    """
    results = []
    cdn_base = get_cdn_url(storage_zone)

    for file_path in sorted(local_dir.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        remote_path = f"{remote_prefix}/{file_path.name}"
        cdn_url = f"{cdn_base}/{remote_path}"

        if dry_run:
            results.append({
                "local_path": str(file_path),
                "remote_path": remote_path,
                "cdn_url": cdn_url,
                "success": True,
                "message": "dry-run",
            })
            print(f"  [dry-run] {file_path.name} → {cdn_url}")
        else:
            success, message = upload_file(file_path, remote_path, storage_zone, password)
            results.append({
                "local_path": str(file_path),
                "remote_path": remote_path,
                "cdn_url": cdn_url if success else None,
                "success": success,
                "message": message,
            })
            status = "✓" if success else "✗"
            print(f"  [{status}] {file_path.name} → {cdn_url if success else message}")

    return results


def update_manifest_with_urls(manifest_path: Path, upload_results: list[dict]) -> bool:
    """Update manifest.json with CDN URLs.

    Adds a 'cdn_urls' section mapping output files to their CDN URLs.
    """
    if not manifest_path.exists():
        return False

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Build URL mapping from results
        url_map = {}
        for result in upload_results:
            if result["success"] and result["cdn_url"]:
                filename = Path(result["local_path"]).name
                url_map[filename] = result["cdn_url"]

        # Add to manifest
        manifest["cdn_urls"] = url_map

        # Also update individual generation entries
        for gen in manifest.get("generations", []):
            output_file = gen.get("output_file")
            if output_file and output_file in url_map:
                gen["cdn_url"] = url_map[output_file]

        # Update icon sheet if present
        if manifest.get("icon_sheet") and manifest["icon_sheet"].get("output_file"):
            icon_file = manifest["icon_sheet"]["output_file"]
            if icon_file in url_map:
                manifest["icon_sheet"]["cdn_url"] = url_map[icon_file]

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return True

    except (json.JSONDecodeError, IOError) as e:
        print(f"Error updating manifest: {e}", file=sys.stderr)
        return False


# --------------- CLI ---------------


def main():
    parser = argparse.ArgumentParser(
        description="Upload files to Bunny CDN Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to upload",
    )
    parser.add_argument(
        "--remote",
        help="Custom remote path (for single file uploads)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without uploading",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--update-manifest",
        action="store_true",
        help="Update manifest.json with CDN URLs (for directory uploads)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Validate environment
    storage_zone = STORAGE_ZONE
    password = STORAGE_PASSWORD

    if not storage_zone:
        print("Error: BUNNY_STORAGE_ZONE environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not password and not args.dry_run:
        print("Error: BUNNY_STORAGE_PASSWORD environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Validate path
    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    cdn_base = get_cdn_url(storage_zone)

    if args.verbose:
        print(f"Storage Zone: {storage_zone}")
        print(f"Storage Host: {STORAGE_API_BASE}")
        print(f"CDN URL: {cdn_base}")
        print()

    results = []

    if args.path.is_file():
        # Single file upload
        if args.remote:
            remote_path = args.remote
        else:
            # Default: use relative path from current dir
            remote_path = str(args.path)

        cdn_url = f"{cdn_base}/{remote_path}"

        if args.dry_run:
            print(f"[dry-run] {args.path} → {cdn_url}")
            results.append({
                "local_path": str(args.path),
                "remote_path": remote_path,
                "cdn_url": cdn_url,
                "success": True,
                "message": "dry-run",
            })
        else:
            print(f"Uploading {args.path}...")
            success, message = upload_file(args.path, remote_path, storage_zone, password)
            results.append({
                "local_path": str(args.path),
                "remote_path": remote_path,
                "cdn_url": cdn_url if success else None,
                "success": success,
                "message": message,
            })
            if success:
                print(f"  ✓ {cdn_url}")
            else:
                print(f"  ✗ {message}")

    elif args.path.is_dir():
        # Directory upload
        remote_prefix = str(args.path).replace("\\", "/")

        print(f"Uploading directory: {args.path}")
        results = upload_directory(
            args.path,
            remote_prefix,
            storage_zone,
            password,
            dry_run=args.dry_run,
        )

        # Summary
        successful = sum(1 for r in results if r["success"])
        print(f"\nUploaded {successful}/{len(results)} files")

        # Update manifest if requested
        if args.update_manifest:
            manifest_path = args.path / "manifest.json"
            if manifest_path.exists():
                if update_manifest_with_urls(manifest_path, results):
                    print(f"Updated: {manifest_path}")
                else:
                    print(f"Failed to update: {manifest_path}")

    # JSON output
    if args.json:
        print(json.dumps(results, indent=2))

    # Exit code
    all_success = all(r["success"] for r in results)
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
