#!/usr/bin/env python3
"""
Generate sample images from all poster scripts for comparison testing.

Runs each script with typical use cases and collects outputs into media/samples/.
Then generates an HTML gallery for easy comparison.

Usage:
  # Run all tests
  python scripts/posters/test-all-scripts.py

  # Run specific script tests
  python scripts/posters/test-all-scripts.py --only generate-ai-image
  python scripts/posters/test-all-scripts.py --only illustrate

  # Dry run - show what would be generated
  python scripts/posters/test-all-scripts.py --dry-run

  # Skip image generation, just rebuild HTML from existing samples
  python scripts/posters/test-all-scripts.py --html-only

  # Use specific date
  python scripts/posters/test-all-scripts.py -d 2026-01-02
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, date

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
SAMPLES_DIR = WORKSPACE_ROOT / "media" / "samples"
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"

# Script definitions with test configurations
SCRIPTS = {
    "illustrate": {
        "file": "illustrate.py",
        "description": "Staff Illustrator - Config-driven rules engine for production batches",
        "features": [
            "Date-seeded determinism",
            "Character reference sheets",
            "Holiday/seasonal detection",
            "Creative brief system",
            "Interactive & batch modes",
        ],
        "tests": [
            {
                "name": "batch-all",
                "args": ["-f", "{facts}", "--batch"],
                "description": "Batch mode - generates all category visuals",
            },
            {
                "name": "with-icons",
                "args": ["-f", "{facts}", "--batch", "--with-icons"],
                "description": "Batch mode with entity icon integration",
            },
            # Style variations - single character scenes
            {
                "name": "style-editorial",
                "args": ["eliza", "-f", "{facts}", "-s", "editorial"],
                "description": "Editorial - New Yorker/Monocle conceptual style",
            },
            {
                "name": "style-cinematic-anime",
                "args": ["eliza", "-f", "{facts}", "-s", "cinematic_anime"],
                "description": "Cinematic anime - Makoto Shinkai atmospheric style",
            },
            {
                "name": "style-comic-panel",
                "args": ["eliza", "shaw", "-f", "{facts}", "-s", "comic_panel"],
                "description": "Comic panel - manga style with action lines",
            },
            {
                "name": "style-noir-ink",
                "args": ["spartan", "-f", "{facts}", "-s", "noir_ink"],
                "description": "Noir ink - high contrast dramatic lighting",
            },
            {
                "name": "style-synthwave",
                "args": ["eliza", "-f", "{facts}", "-s", "synthwave"],
                "description": "Synthwave - 80s retrofuturism neon grids",
            },
            {
                "name": "style-ukiyo-e",
                "args": ["eliza", "-f", "{facts}", "-s", "ukiyo_e"],
                "description": "Ukiyo-e - traditional Japanese woodblock style",
            },
            {
                "name": "style-cyberpunk-hud",
                "args": ["shaw", "-f", "{facts}", "-s", "cyberpunk_hud"],
                "description": "Cyberpunk HUD - holographic interface aesthetic",
            },
            {
                "name": "style-dataviz",
                "args": ["-f", "{facts}", "-s", "dataviz", "--batch"],
                "description": "Data visualization - charts and infographics (no characters)",
            },
            {
                "name": "style-isometric-city",
                "args": ["-f", "{facts}", "-s", "isometric_city", "--batch"],
                "description": "Isometric city - modular architecture diorama",
            },
        ],
    },
    "illustrate-adaptive": {
        "file": "illustrate-adaptive.py",
        "description": "Technical Artist - LLM content analyzer with format-agnostic input",
        "features": [
            "Content fingerprinting",
            "Dynamic scene generation",
            "Entity extraction",
            "Icon integration support",
        ],
        "tests": [
            {
                "name": "facts-json",
                "args": ["{facts}", "-n", "4"],
                "description": "Analyze facts JSON - generate 4 illustrations",
            },
            {
                "name": "with-icons",
                "args": ["{facts}", "-n", "4", "--with-icons"],
                "description": "With entity icon extraction and integration",
            },
            # Different input format tests
            {
                "name": "markdown-facts",
                "args": ["{facts_md}", "-n", "4"],
                "description": "Analyze markdown file - format agnostic test",
            },
            {
                "name": "retro-json",
                "args": ["{retro}", "-n", "4"],
                "description": "Analyze monthly retro JSON - long-form content",
            },
        ],
    },
    "scene_director": {
        "file": "scene_director.py",
        "description": "Editorial Director - LLM creative director for cohesive visual storytelling",
        "features": [
            "Unified day aesthetic",
            "Visual metaphors (never literal)",
            "Character casting",
            "4-scene narrative sets",
        ],
        "tests": [
            {
                "name": "editorial-set",
                "args": ["{facts}"],
                "description": "Full 4-scene editorial set with LLM-chosen style",
            },
            {
                "name": "style-override",
                "args": ["{facts}", "--style", "Warm Industrial"],
                "description": "4-scene set with manual style override",
            },
        ],
    },
    "create-tag-icons": {
        "file": "create-tag-icons.py",
        "description": "Icon Generator - Create icons from tag words with humor prefixes",
        "features": [
            "Minimal prompts",
            "1024x1024 square output",
            "Archetype-based prefixes",
            "Stock/intern/idiomatic/literal modes",
        ],
        "tests": [
            {
                "name": "stock-prefix",
                "args": ["blockchain", "-p", "stock"],
                "description": "Stock photo misunderstanding of 'blockchain'",
            },
            {
                "name": "intern-prefix",
                "args": ["tokenomics", "-p", "intern"],
                "description": "Overconfident intern interpretation of 'tokenomics'",
            },
            {
                "name": "literal-prefix",
                "args": ["governance", "-p", "literal"],
                "description": "Literal but wrong interpretation of 'governance'",
            },
            {
                "name": "idiomatic-prefix",
                "args": ["decentralized", "-p", "idiomatic"],
                "description": "Idiomatic literal interpretation of 'decentralized'",
            },
            {
                "name": "random-prefix",
                "args": ["{random_tag}", "-p", "random"],
                "description": "Random prefix with dynamically selected tag from facts",
            },
            # Batch generation from facts
            {
                "name": "from-facts",
                "args": ["--from-facts", "-p", "random", "--skip-existing"],
                "description": "Batch generate icons for all tags from facts files",
            },
        ],
    },
}


def get_latest_facts_date() -> str:
    """Find the most recent facts file date."""
    facts_files = sorted(FACTS_DIR.glob("2*.json"), reverse=True)
    if facts_files:
        return facts_files[0].stem
    return date.today().isoformat()


def get_random_tag_from_facts(facts_path: Path) -> str:
    """Extract a random tag from facts file for testing."""
    import random
    try:
        data = json.loads(facts_path.read_text())
        tags = set()
        tags_obj = data.get("tags", {})
        for key in ["themes", "derived", "story_type"]:
            for tag in tags_obj.get(key, []):
                if isinstance(tag, str) and tag.strip() and len(tag) < 20:
                    tags.add(tag.strip())
        if tags:
            return random.choice(list(tags))
    except Exception:
        pass
    return "innovation"  # fallback


def get_latest_retro_path() -> Path:
    """Find the most recent monthly retro file."""
    retros_dir = WORKSPACE_ROOT / "the-council" / "retros"
    retro_files = sorted(retros_dir.glob("*-retro.json"), reverse=True)
    if retro_files:
        return retro_files[0]
    # Fallback to a specific retro if none found
    return retros_dir / "2025-01-retro.json"


def get_all_pngs_with_mtime(directories: list) -> dict:
    """Get all PNG files with their mtimes in given directories."""
    pngs = {}
    for d in directories:
        if d.exists():
            for img in d.rglob("*.png"):
                pngs[img] = img.stat().st_mtime
    return pngs


def find_new_or_modified_pngs(before: dict, after: dict) -> set:
    """Find PNGs that are new or have been modified."""
    result = set()
    for path, mtime in after.items():
        if path not in before:
            result.add(path)  # New file
        elif mtime > before[path]:
            result.add(path)  # Modified file
    return result


def run_script(script_name: str, test_config: dict, date_str: str, dry_run: bool = False) -> dict:
    """Run a single test configuration for a script."""
    script_info = SCRIPTS[script_name]
    script_path = SCRIPT_DIR / script_info["file"]

    # Prepare arguments with variable substitution
    facts_path = FACTS_DIR / f"{date_str}.json"
    facts_md_path = WORKSPACE_ROOT / "hackmd" / "facts" / f"{date_str}.md"
    retro_path = get_latest_retro_path()  # Use latest retro for long-form content test
    random_tag = None  # Lazy load only if needed
    args = []
    for arg in test_config["args"]:
        arg = arg.replace("{date}", date_str)
        arg = arg.replace("{facts}", str(facts_path))
        arg = arg.replace("{facts_md}", str(facts_md_path))
        arg = arg.replace("{retro}", str(retro_path))
        if "{random_tag}" in arg:
            if random_tag is None:
                random_tag = get_random_tag_from_facts(facts_path)
            arg = arg.replace("{random_tag}", random_tag)
        args.append(arg)

    test_name = test_config["name"]
    output_dir = SAMPLES_DIR / script_name / test_name

    result = {
        "script": script_name,
        "test": test_name,
        "description": test_config["description"],
        "command": f"python {script_path.name} {' '.join(args)}",
        "output_dir": str(output_dir),
        "images": [],
        "status": "pending",
        "error": None,
        "stdout": "",
    }

    if dry_run:
        print(f"  [DRY RUN] {script_name}/{test_name}")
        print(f"    Command: {result['command']}")
        result["status"] = "dry_run"
        return result

    print(f"  Running: {script_name}/{test_name}...")

    # Clean and create output directory (ensures fresh detection)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Track existing PNGs before running (with mtimes to detect overwrites)
    # Include all potential output directories
    watch_dirs = [
        WORKSPACE_ROOT / "media",  # Covers media/quick/, media/daily/, media/editorial/, media/samples/
        output_dir,  # The samples output directory
        SCRIPT_DIR / "assets" / "icons",  # Entity icons
    ]
    before_pngs = get_all_pngs_with_mtime(watch_dirs)

    try:
        # Build command with output override where possible
        cmd = ["python", str(script_path)] + args

        # Add output directory override for scripts that support it
        if script_name in ["create-tag-icons", "scene_director"]:
            cmd.extend(["-o", str(output_dir)])

        # Run with timeout
        env = os.environ.copy()
        proc = subprocess.run(
            cmd,
            cwd=WORKSPACE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        result["stdout"] = proc.stdout[-2000:] if proc.stdout else ""
        result["stderr"] = proc.stderr[-2000:] if proc.stderr else ""

        if proc.returncode != 0:
            result["status"] = "error"
            result["error"] = proc.stderr[-500:] if proc.stderr else "Unknown error"
            print(f"    ERROR: {result['error'][:100]}...")
            print(f"    STDOUT: {proc.stdout[-200:] if proc.stdout else '(none)'}")
        else:
            result["status"] = "success"

            # Find new or modified images by comparing before/after mtimes
            after_pngs = get_all_pngs_with_mtime(watch_dirs)
            new_pngs = find_new_or_modified_pngs(before_pngs, after_pngs)

            # Copy new images and their prompts to samples directory
            sample_images = []
            for img in sorted(new_pngs):
                dest = output_dir / img.name
                if img.resolve() != dest.resolve() and not dest.exists():
                    shutil.copy2(img, dest)
                # Also copy prompt file if it exists (same name but .txt)
                prompt_file = img.with_suffix(".txt")
                prompt_dest = output_dir / prompt_file.name
                if prompt_file.exists() and prompt_file.resolve() != prompt_dest.resolve():
                    shutil.copy2(prompt_file, prompt_dest)
                # Use path relative to SAMPLES_DIR for gallery (works for file:// and http server)
                sample_images.append(str(dest.relative_to(SAMPLES_DIR)))

            result["images"] = sample_images
            if len(sample_images) == 0:
                result["status"] = "warning"
                print(f"    WARNING: No images generated")
            else:
                print(f"    Generated {len(result['images'])} images")

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Script timed out after 5 minutes"
        print(f"    TIMEOUT")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"    ERROR: {e}")

    return result




def generate_html_gallery(results: list, date_str: str) -> str:
    """Generate HTML gallery for comparing script outputs."""

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poster Scripts Comparison - {date_str}</title>
    <style>
        :root {{
            --bg: #1a1a2e;
            --surface: #16213e;
            --border: #0f3460;
            --text: #e8e8e8;
            --accent: #00d9ff;
            --success: #00ff88;
            --error: #ff4757;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'SF Mono', 'Consolas', monospace;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            line-height: 1.6;
        }}

        h1 {{
            color: var(--accent);
            margin-bottom: 0.5rem;
            font-size: 1.8rem;
        }}

        .subtitle {{
            color: #888;
            margin-bottom: 2rem;
        }}

        .script-section {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 2rem;
            overflow: hidden;
        }}

        .script-header {{
            background: var(--border);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
        }}

        .script-name {{
            color: var(--accent);
            font-size: 1.2rem;
            font-weight: bold;
        }}

        .script-file {{
            color: #888;
            font-size: 0.85rem;
        }}

        .script-description {{
            margin-top: 0.5rem;
            color: var(--text);
        }}

        .features {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }}

        .feature {{
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid rgba(0, 217, 255, 0.3);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            color: var(--accent);
        }}

        .tests-container {{
            padding: 1.5rem;
        }}

        .test-section {{
            margin-bottom: 1.5rem;
        }}

        .test-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.75rem;
        }}

        .test-name {{
            color: var(--success);
            font-weight: bold;
        }}

        .test-status {{
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}

        .test-status.success {{ background: rgba(0, 255, 136, 0.2); color: var(--success); }}
        .test-status.warning {{ background: rgba(255, 193, 7, 0.2); color: #ffc107; }}
        .test-status.error {{ background: rgba(255, 71, 87, 0.2); color: var(--error); }}
        .test-status.pending {{ background: rgba(255, 255, 255, 0.1); color: #888; }}

        .test-description {{
            color: #aaa;
            font-size: 0.85rem;
            margin-bottom: 0.5rem;
        }}

        .test-command {{
            background: var(--bg);
            padding: 0.5rem 0.75rem;
            border-radius: 4px;
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 1rem;
            overflow-x: auto;
        }}

        .image-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }}

        .image-card {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .image-card:hover {{
            transform: scale(1.02);
            border-color: var(--accent);
        }}

        .image-card img {{
            width: 100%;
            height: 150px;
            object-fit: cover;
            display: block;
        }}

        .image-card .image-name {{
            padding: 0.5rem;
            font-size: 0.7rem;
            color: #888;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .no-images {{
            color: #666;
            font-style: italic;
            padding: 1rem;
            text-align: center;
        }}

        /* Lightbox */
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}

        .lightbox.active {{
            display: flex;
        }}

        .lightbox img {{
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }}

        .lightbox-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            color: white;
            font-size: 2rem;
            cursor: pointer;
            padding: 0.5rem;
        }}

        .lightbox-info {{
            position: absolute;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            background: rgba(0, 0, 0, 0.7);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.85rem;
        }}

        .error-message {{
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid var(--error);
            color: var(--error);
            padding: 0.75rem;
            border-radius: 4px;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }}
    </style>
</head>
<body>
    <h1>Poster Scripts Comparison</h1>
    <p class="subtitle">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Facts date: {date_str}</p>

    <div class="script-section">
        <div class="script-header">
            <div class="script-name">Character References</div>
            <div class="script-description">Reference sheets used for character consistency</div>
        </div>
        <div class="tests-container">
            <div class="image-gallery">
'''

    # Add character reference sheets (copy to samples dir for HTTP server compatibility)
    characters_dir = SCRIPT_DIR / "characters"
    char_samples_dir = SAMPLES_DIR / "characters"
    char_samples_dir.mkdir(parents=True, exist_ok=True)

    for char_dir in sorted(characters_dir.iterdir()):
        if char_dir.is_dir() and not char_dir.name.startswith("."):
            char_name = char_dir.name
            ref_sheet = char_dir / f"reference-sheet-{char_name}.png"
            if ref_sheet.exists():
                # Copy to samples directory
                dest = char_samples_dir / f"reference-sheet-{char_name}.png"
                if not dest.exists() or ref_sheet.stat().st_mtime > dest.stat().st_mtime:
                    shutil.copy2(ref_sheet, dest)
                rel_path = f"characters/reference-sheet-{char_name}.png"
                html += f'''                <div class="image-card" onclick="openLightbox('{rel_path}', '{char_name}')">
                    <img src="{rel_path}" alt="{char_name}" loading="lazy">
                    <div class="image-name">{char_name}</div>
                </div>
'''

    html += '''            </div>
        </div>
    </div>
'''

    # Group results by script
    by_script = {}
    for result in results:
        script = result["script"]
        if script not in by_script:
            by_script[script] = []
        by_script[script].append(result)

    # Generate sections for each script
    for script_name, script_info in SCRIPTS.items():
        script_results = by_script.get(script_name, [])

        html += f'''
    <div class="script-section">
        <div class="script-header">
            <div class="script-name">{script_name}</div>
            <div class="script-file">{script_info["file"]}</div>
            <div class="script-description">{script_info["description"]}</div>
            <div class="features">
'''
        for feature in script_info.get("features", []):
            html += f'                <span class="feature">{feature}</span>\n'

        html += '''            </div>
        </div>
        <div class="tests-container">
'''

        if not script_results and not script_info.get("tests"):
            html += '            <div class="no-images">No tests configured for this script</div>\n'
        elif not script_results:
            html += '            <div class="no-images">Tests not run yet</div>\n'
        else:
            for result in script_results:
                status_class = result["status"]
                html += f'''
            <div class="test-section">
                <div class="test-header">
                    <span class="test-name">{result["test"]}</span>
                    <span class="test-status {status_class}">{status_class}</span>
                </div>
                <div class="test-description">{result["description"]}</div>
                <div class="test-command">$ {result["command"]}</div>
'''

                if result.get("error"):
                    html += f'                <div class="error-message">{result["error"][:200]}</div>\n'

                if result.get("images"):
                    html += '                <div class="image-gallery">\n'
                    for img_path in result["images"]:
                        img_name = Path(img_path).name
                        html += f'''                    <div class="image-card" onclick="openLightbox('{img_path}', '{img_name}')">
                        <img src="{img_path}" alt="{img_name}" loading="lazy">
                        <div class="image-name">{img_name}</div>
                    </div>
'''
                    html += '                </div>\n'
                else:
                    html += '                <div class="no-images">No images generated</div>\n'

                html += '            </div>\n'

        html += '''        </div>
    </div>
'''

    html += '''
    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <span class="lightbox-close">&times;</span>
        <span class="lightbox-nav lightbox-prev" onclick="event.stopPropagation(); navigateLightbox(-1)">&#10094;</span>
        <div class="lightbox-content" onclick="event.stopPropagation()">
            <img id="lightbox-img" src="" alt="">
            <div class="lightbox-info" id="lightbox-info"></div>
            <div class="lightbox-prompt" id="lightbox-prompt"></div>
        </div>
        <span class="lightbox-nav lightbox-next" onclick="event.stopPropagation(); navigateLightbox(1)">&#10095;</span>
    </div>

    <style>
        .lightbox-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 3rem;
            cursor: pointer;
            padding: 1rem;
            user-select: none;
            opacity: 0.7;
            transition: opacity 0.2s;
            z-index: 10;
        }
        .lightbox-nav:hover { opacity: 1; }
        .lightbox-prev { left: 1rem; }
        .lightbox-next { right: 1rem; }
        .lightbox-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 90%;
            max-height: 90%;
        }
        .lightbox-content img {
            max-width: 100%;
            max-height: 70vh;
            object-fit: contain;
        }
        .lightbox-prompt {
            background: rgba(0, 0, 0, 0.8);
            color: #aaa;
            padding: 1rem;
            margin-top: 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            max-width: 800px;
            max-height: 150px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            text-align: left;
        }
        .lightbox-prompt:empty {
            display: none;
        }
    </style>

    <script>
        // Collect all images for navigation
        const allImages = Array.from(document.querySelectorAll('.image-card')).map(card => ({
            src: card.querySelector('img').src,
            name: card.querySelector('.image-name').textContent
        }));
        let currentIndex = 0;

        async function loadPrompt(imgSrc) {
            const promptPath = imgSrc.replace(/\\.png$/i, '.txt');
            try {
                const response = await fetch(promptPath);
                if (response.ok) {
                    return await response.text();
                }
            } catch (e) {}
            return '';
        }

        async function openLightbox(src, name) {
            currentIndex = allImages.findIndex(img => img.src.endsWith(src) || src.endsWith(img.src.split('/').pop()));
            if (currentIndex === -1) currentIndex = 0;
            document.getElementById('lightbox-img').src = src;
            document.getElementById('lightbox-info').textContent = name + ' (' + (currentIndex + 1) + '/' + allImages.length + ')';
            document.getElementById('lightbox').classList.add('active');

            // Load and display prompt
            const prompt = await loadPrompt(src);
            document.getElementById('lightbox-prompt').textContent = prompt;
        }

        function closeLightbox(event) {
            if (event && (event.target.tagName === 'IMG' || event.target.classList.contains('lightbox-content'))) return;
            document.getElementById('lightbox').classList.remove('active');
        }

        async function navigateLightbox(direction) {
            currentIndex = (currentIndex + direction + allImages.length) % allImages.length;
            const img = allImages[currentIndex];
            document.getElementById('lightbox-img').src = img.src;
            document.getElementById('lightbox-info').textContent = img.name + ' (' + (currentIndex + 1) + '/' + allImages.length + ')';

            // Load and display prompt
            const prompt = await loadPrompt(img.src);
            document.getElementById('lightbox-prompt').textContent = prompt;
        }

        document.addEventListener('keydown', (e) => {
            const lightbox = document.getElementById('lightbox');
            if (!lightbox.classList.contains('active')) return;

            if (e.key === 'Escape') closeLightbox();
            else if (e.key === 'ArrowLeft') navigateLightbox(-1);
            else if (e.key === 'ArrowRight') navigateLightbox(1);
        });
    </script>
</body>
</html>
'''

    return html


def main():
    parser = argparse.ArgumentParser(description="Test all poster scripts and generate comparison gallery")
    parser.add_argument("-d", "--date", help="Date for facts file (default: latest)")
    parser.add_argument("--only", help="Only run tests for specific script")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--html-only", action="store_true", help="Only regenerate HTML from existing samples")
    args = parser.parse_args()

    # Determine date
    date_str = args.date or get_latest_facts_date()
    facts_path = FACTS_DIR / f"{date_str}.json"

    if not facts_path.exists() and not args.html_only:
        print(f"Error: Facts file not found: {facts_path}")
        sys.exit(1)

    print(f"Poster Scripts Test Suite")
    print(f"Date: {date_str}")
    print(f"Facts: {facts_path}")
    print("=" * 60)

    results = []

    if not args.html_only:
        # Create samples directory
        SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

        # Run tests for each script
        for script_name, script_info in SCRIPTS.items():
            if args.only and args.only != script_name:
                continue

            tests = script_info.get("tests", [])
            if not tests:
                print(f"\n{script_name}: No tests configured, skipping")
                continue

            print(f"\n{script_name}:")

            for test_config in tests:
                result = run_script(script_name, test_config, date_str, args.dry_run)
                results.append(result)

        # Save results JSON
        results_path = SAMPLES_DIR / "results.json"
        with open(results_path, "w") as f:
            json.dump({"date": date_str, "results": results}, f, indent=2)
        print(f"\nResults saved: {results_path}")

    else:
        # Load existing results
        results_path = SAMPLES_DIR / "results.json"
        if results_path.exists():
            with open(results_path) as f:
                data = json.load(f)
                results = data.get("results", [])
                date_str = data.get("date", date_str)

        # Scan for images in samples directory
        for script_name in SCRIPTS:
            script_dir = SAMPLES_DIR / script_name
            if script_dir.exists():
                for test_dir in script_dir.iterdir():
                    if test_dir.is_dir():
                        images = [
                            str(img.relative_to(SAMPLES_DIR))
                            for img in test_dir.glob("*.png")
                        ]
                        # Find or create result entry
                        found = False
                        for r in results:
                            if r["script"] == script_name and r["test"] == test_dir.name:
                                r["images"] = images
                                # Update status based on images found
                                if images:
                                    r["status"] = "success"
                                    r["error"] = None
                                found = True
                                break
                        if not found and images:
                            results.append({
                                "script": script_name,
                                "test": test_dir.name,
                                "description": "",
                                "command": "",
                                "images": images,
                                "status": "success",
                            })

        # Save updated results
        with open(results_path, "w") as f:
            json.dump({"date": date_str, "results": results}, f, indent=2)

    # Generate HTML gallery
    html = generate_html_gallery(results, date_str)
    html_path = SAMPLES_DIR / "gallery.html"
    html_path.write_text(html)
    print(f"Gallery saved: {html_path}")

    # Summary
    print("\n" + "=" * 60)
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    warnings = sum(1 for r in results if r["status"] == "warning")
    errors = sum(1 for r in results if r["status"] == "error")
    summary = f"Tests: {success}/{total} successful"
    if warnings:
        summary += f", {warnings} warnings"
    if errors:
        summary += f", {errors} errors"
    print(summary)
    print(f"Gallery: file://{html_path.absolute()}")


if __name__ == "__main__":
    main()
