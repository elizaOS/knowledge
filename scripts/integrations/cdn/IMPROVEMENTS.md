# CDN Pipeline - Improvement Notes

Code review of the quickly-written CDN upload pipeline. These are potential improvements for future iterations.

## upload.py

### DRY Violations

1. **Duplicate result-building logic** (lines 135-153 vs 283-303)
   - Single file and directory upload both build similar result dicts
   - Extract to a helper: `build_result(local_path, remote_path, cdn_url, success, message)`

2. **Duplicate dry-run printing logic**
   - Both paths have similar print statements for dry-run
   - Consider a unified `log_upload_result(result, dry_run=False)` function

### Security

1. **Path validation** - Currently trusts input paths
   - Add: `remote_path = remote_path.lstrip("/")` to prevent absolute paths
   - Consider validating no `..` in paths (path traversal)
   ```python
   if ".." in remote_path or remote_path.startswith("/"):
       raise ValueError(f"Invalid remote path: {remote_path}")
   ```

2. **File size limits** - No protection against uploading huge files
   - Add max file size check before upload
   - Bunny has limits; we should enforce locally first

### Maintainability

1. **Config class** - Global vars at module level are harder to test
   ```python
   @dataclass
   class BunnyConfig:
       storage_zone: str
       storage_host: str
       cdn_url: str
       password: str = field(repr=False)  # Don't log password

       @classmethod
       def from_env(cls) -> "BunnyConfig":
           ...
   ```

2. **Hardcoded defaults** - `m3tv` and `la.storage` are project-specific
   - Move to a config file or require env vars without defaults
   - Or: use a `.env` file pattern with `python-dotenv`

3. **No retry logic** - Network failures will just fail
   - Add exponential backoff for transient failures
   - `tenacity` library or simple retry loop

4. **No concurrent uploads** - Sequential is slow for many files
   - Use `concurrent.futures.ThreadPoolExecutor` for parallel uploads
   - Be mindful of rate limits

### Error Handling

1. **Silent manifest update failure** - Returns False but continues
   - Should this be fatal? At least log more details

2. **Generic exception catching** - `except (json.JSONDecodeError, IOError)`
   - Consider more specific handling per error type

### Testing

1. **No unit tests** - Functions aren't easily testable
   - Extract HTTP logic to allow mocking
   - Add `tests/test_cdn_upload.py`

---

## update_facts_media.py

### DRY Violations

1. **Duplicated JSON read/write pattern** with upload.py
   - Extract to shared utility: `scripts/integrations/utils/json_utils.py`

### Security

1. **No backup before overwriting facts.json**
   - Consider: write to `.tmp`, then atomic rename
   - Or: create `.bak` file first

### Maintainability

1. **Hardcoded path patterns** - `source_manifest` stores full path
   - Should store relative path for portability

2. **No schema validation** - Trusts manifest structure
   - Add basic validation that required keys exist

---

## generate-illustrations.yml (Workflow)

### Security

1. **Shell injection risk** in date handling (line 90)
   ```yaml
   FACTS_DATE=$(python3 -c "import json; print(json.load(open('${FACTS_FILE}'))['briefing_date'])")
   ```
   - If `FACTS_FILE` contained special chars, could break
   - Better: use proper quoting or a dedicated script

2. **Hardcoded CDN URL in summary** (line 181)
   - Should use variable/output, not hardcoded `m3tv.b-cdn.net`

### Maintainability

1. **No input validation** - `facts_date` input isn't validated as date format
   - Add a validation step before using

2. **Long conditional chains** (line 136)
   ```yaml
   if: inputs.update_facts == 'true' && inputs.upload_to_cdn == 'true' && inputs.dry_run == 'false' && steps.generate.outputs.generated == 'true'
   ```
   - Hard to read; consider job-level conditionals or a composite action

3. **Missing error handling** - What if upload succeeds but facts update fails?
   - Consider: should we still commit the posters?
   - Add explicit failure handling per step

### DRY Violations

1. **Repeated path construction**
   - `${{ steps.facts.outputs.output_dir }}` vs `${{ steps.facts.outputs.output_dir_rel }}`
   - Could simplify by always using relative and constructing absolute when needed

---

## illustrate.py (batch_mode changes)

### Quick review of additions:

1. **Good**: Manifest tracks useful metadata
2. **Good**: Timing per generation helps identify slow steps

### Potential improvements:

1. **content_context truncation** - Hardcoded `[:500]`
   - Make configurable or document why 500

2. **No manifest schema versioning strategy**
   - Version "1.0" is good, but no migration plan documented

---

## General Improvements

### Add shared utilities

```
scripts/integrations/
├── cdn/
│   ├── upload.py
│   └── update_facts_media.py
└── utils/
    ├── __init__.py
    ├── json_utils.py      # read/write JSON with error handling
    ├── retry.py           # retry decorator
    └── validation.py      # path validation, schema checks
```

### Configuration management

Consider a unified config approach:
```python
# scripts/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    bunny_storage_zone: str
    bunny_storage_host: str
    bunny_storage_password: str
    bunny_cdn_url: str

    class Config:
        env_file = ".env"
```

### Add integration tests

```bash
# Test the full pipeline locally
./scripts/test_cdn_pipeline.sh --dry-run
```

---

## Priority Matrix

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Path validation (security) | High | Low | **P0** |
| Retry logic | Medium | Medium | P1 |
| Config class refactor | Medium | Medium | P1 |
| Concurrent uploads | Medium | Medium | P2 |
| Unit tests | Medium | High | P2 |
| Shared utilities | Low | Medium | P3 |
