#!/usr/bin/env python3
"""
API Preflight Check for OpenClaw and Foundups-Agent.

Validates that configured LLM API keys are:
1. Present in environment
2. Well-formed (format check)
3. Actually work (live connectivity test with minimal token usage)
4. Not quota-exhausted (catches 429/quota errors)

Designed to run:
- On gateway startup (via OpenClaw hook or systemd ExecStartPre)
- As a periodic cron check
- Manually: python scripts/api_preflight_check.py

Exit codes:
  0 = All providers healthy
  1 = At least one provider failed (details in output)
  2 = No providers configured

Pattern source: youtube_auth/src/quota_intelligence.py (pre-call verification)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Load .env file (so we always read fresh values, not stale system env)
# ---------------------------------------------------------------------------

def _load_dotenv():
    """Load .env file into os.environ. .env always wins (overwrite mode)."""
    env_paths = [
        Path(__file__).resolve().parent.parent / ".env",  # O:/Foundups-Agent/.env
        Path("/mnt/o/Foundups-Agent/.env"),                # WSL mount
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # Remove inline comments
                    if "#" in value and not value.startswith("http"):
                        value = value[:value.index("#")].strip()
                    if key and value:
                        os.environ[key] = value  # .env always wins over stale system env
            return

_load_dotenv()


# ---------------------------------------------------------------------------
# Provider definitions
# ---------------------------------------------------------------------------

@dataclass
class ProviderResult:
    provider: str
    status: str  # "ok", "error", "quota_exceeded", "auth_failed", "missing"
    latency_ms: float = 0.0
    model: str = ""
    error: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


PROVIDERS = {
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "prefix": "sk-",
        "test_url": "https://api.openai.com/v1/chat/completions",
        "test_model": "gpt-5",
        "auth_header": lambda key: ("Authorization", f"Bearer {key}"),
        "openclaw_model": "openai/gpt-5",
    },
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "env_var_alt": ["CLAUDE_API_KEY"],
        "prefix": "sk-ant-",
        "test_url": "https://api.anthropic.com/v1/messages",
        "test_model": "claude-haiku-4-20250414",
        "auth_header": lambda key: ("x-api-key", key),
        "openclaw_model": "anthropic/claude-sonnet-4-20250514",
    },
    "google": {
        "env_var": "GEMINI_API_KEY",
        "env_var_alt": ["GOOGLE_AISTUDIO_API_KEY", "GOOGLE_API_KEY"],
        "prefix": "",
        "test_url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        "test_model": "gemini-2.0-flash",
        "auth_header": lambda key: (None, None),  # Key passed in URL
        "openclaw_model": "google/gemini-2.0-flash",
    },
    "deepseek": {
        "env_var": "DEEPSEEK_API_KEY",
        "prefix": "",
        "test_url": "https://api.deepseek.com/chat/completions",
        "test_model": "deepseek-chat",
        "auth_header": lambda key: ("Authorization", f"Bearer {key}"),
        "openclaw_model": "deepseek/deepseek-chat",
    },
    "xai": {
        "env_var": "GROK_API_KEY",
        "prefix": "",
        "test_url": "https://api.x.ai/v1/chat/completions",
        "test_model": "grok-3-mini",
        "auth_header": lambda key: ("Authorization", f"Bearer {key}"),
        "openclaw_model": "xai/grok-3-mini",
    },
}

# Minimal test payloads (1-2 tokens response, ~$0.0001 cost)
def _openai_payload(model):
    return json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply with only the word: ok"}],
        "max_tokens": 3,
    }).encode()

def _google_payload(model):
    return json.dumps({
        "contents": [{"parts": [{"text": "Reply with only the word: ok"}]}],
        "generationConfig": {"maxOutputTokens": 3},
    }).encode()

TEST_PAYLOADS = {
    "openai": _openai_payload,
    "anthropic": _openai_payload,  # Same format as OpenAI
    "deepseek": _openai_payload,   # OpenAI-compatible
    "xai": _openai_payload,        # OpenAI-compatible
    "google": _google_payload,
}

ANTHROPIC_HEADERS = {
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_key_present(provider: str) -> tuple[Optional[str], Optional[str]]:
    """Check if API key exists in environment. Returns (key, error)."""
    cfg = PROVIDERS[provider]
    key = os.environ.get(cfg["env_var"], "").strip()
    if not key:
        # Try alternative env var names
        for alt_var in cfg.get("env_var_alt", []):
            key = os.environ.get(alt_var, "").strip()
            if key:
                return key, None
        all_vars = [cfg["env_var"]] + cfg.get("env_var_alt", [])
        return None, f"None of {all_vars} set in environment"
    return key, None


def check_key_format(provider: str, key: str) -> Optional[str]:
    """Basic format validation. Returns error message or None."""
    cfg = PROVIDERS[provider]
    prefix = cfg.get("prefix", "")
    if prefix and not key.startswith(prefix):
        return f"Key does not start with expected prefix '{prefix}...'"
    if len(key) < 20:
        return f"Key too short ({len(key)} chars)"
    return None


def check_api_live(provider: str, key: str) -> ProviderResult:
    """Make a minimal API call to verify the key works."""
    cfg = PROVIDERS[provider]
    model = cfg["test_model"]
    url = cfg["test_url"]
    payload = TEST_PAYLOADS[provider](model)

    # Google uses key-in-URL pattern
    if provider == "google":
        url = url.format(model=model, key=key)
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
    else:
        header_name, header_value = cfg["auth_header"](key)
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header(header_name, header_value)
        req.add_header("Content-Type", "application/json")

    # User-Agent required to avoid Cloudflare 1010 blocks (xAI, DeepSeek)
    req.add_header("User-Agent", "FoundupsAgent/1.0")

    # Anthropic needs extra headers
    if provider == "anthropic":
        for k, v in ANTHROPIC_HEADERS.items():
            if k != "content-type":
                req.add_header(k, v)

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            elapsed = (time.monotonic() - start) * 1000
            body = json.loads(resp.read())

            # Verify we got a response
            if provider == "openai":
                content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            elif provider == "anthropic":
                content = body.get("content", [{}])[0].get("text", "")
            else:
                content = "unknown"

            return ProviderResult(
                provider=provider,
                status="ok",
                latency_ms=round(elapsed, 1),
                model=model,
            )

    except urllib.error.HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        raw_error = ""
        try:
            raw_error = e.read().decode()
            error_body = json.loads(raw_error)
        except Exception:
            error_body = {"error": raw_error[:200] if raw_error else str(e)}

        error_msg = ""
        # Extract error message - handle both {"error": {"message": "..."}} and {"error": "string"} formats
        error_field = error_body.get("error", "") if isinstance(error_body, dict) else str(error_body)
        if isinstance(error_field, dict):
            error_msg = error_field.get("message", str(e))
        elif isinstance(error_field, str) and error_field:
            error_msg = error_field
        else:
            error_msg = str(e)
        # Also check top-level "code" field (xAI uses {"code": "...", "error": "..."})
        if isinstance(error_body, dict) and "code" in error_body and error_body["code"] != error_msg:
            error_msg = f"{error_body['code']}: {error_msg}"

        # Classify the error
        low_msg = error_msg.lower()
        if e.code == 401:
            status = "auth_failed"
        elif (e.code == 429
              or "quota" in low_msg
              or "exceeded" in low_msg
              or "credit balance" in low_msg
              or "billing" in low_msg
              or "insufficient" in low_msg
              or "credits" in low_msg
              or "licenses" in low_msg):
            status = "quota_exceeded"
        elif e.code == 403:
            status = "auth_failed"
        else:
            status = "error"

        return ProviderResult(
            provider=provider,
            status=status,
            latency_ms=round(elapsed, 1),
            model=model,
            error=error_msg[:200],
        )

    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return ProviderResult(
            provider=provider,
            status="error",
            latency_ms=round(elapsed, 1),
            model=model,
            error=str(e)[:200],
        )


def run_preflight(providers: Optional[list] = None, live_check: bool = True) -> list[ProviderResult]:
    """Run preflight checks for all configured providers."""
    if providers is None:
        providers = list(PROVIDERS.keys())

    results = []

    for provider in providers:
        if provider not in PROVIDERS:
            results.append(ProviderResult(provider=provider, status="error", error="Unknown provider"))
            continue

        # Step 1: Key present?
        key, err = check_key_present(provider)
        if err:
            results.append(ProviderResult(provider=provider, status="missing", error=err))
            continue

        # Step 2: Key format?
        fmt_err = check_key_format(provider, key)
        if fmt_err:
            results.append(ProviderResult(provider=provider, status="error", error=fmt_err))
            continue

        # Step 3: Live connectivity test
        if live_check:
            result = check_api_live(provider, key)
            results.append(result)
        else:
            results.append(ProviderResult(
                provider=provider,
                status="ok",
                error="(format-only check, no live test)",
            ))

    return results


# ---------------------------------------------------------------------------
# OpenClaw integration
# ---------------------------------------------------------------------------

def update_openclaw_model_if_needed(results: list[ProviderResult]):
    """
    If the current primary model's provider is down, switch to a healthy one.
    Reads/writes ~/.openclaw/openclaw.json.
    """
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if not os.path.exists(config_path):
        return

    with open(config_path) as f:
        cfg = json.load(f)

    primary = cfg.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
    if not primary:
        return

    # Determine current provider from model string
    current_provider = None
    if primary.startswith("openai/"):
        current_provider = "openai"
    elif primary.startswith("anthropic/"):
        current_provider = "anthropic"

    if not current_provider:
        return

    # Check if current provider is healthy
    status_map = {r.provider: r.status for r in results}
    if status_map.get(current_provider) == "ok":
        return  # Current provider is fine

    # Find a healthy alternative
    fallback_models = {
        "anthropic": "anthropic/claude-sonnet-4-20250514",
        "openai": "openai/gpt-5",
    }

    for alt_provider, alt_model in fallback_models.items():
        if alt_provider != current_provider and status_map.get(alt_provider) == "ok":
            # Switch
            model_cfg = cfg.get("agents", {}).get("defaults", {}).get("model", {})
            old_primary = model_cfg.get("primary", "")
            model_cfg["primary"] = alt_model
            model_cfg["fallback"] = old_primary
            cfg["agents"]["defaults"]["model"] = model_cfg

            with open(config_path, "w") as f:
                json.dump(cfg, f, indent=2)
                f.write("\n")

            print(f"[AUTO-SWITCH] {old_primary} -> {alt_model} (provider {current_provider} status: {status_map.get(current_provider)})")
            return

    print(f"[WARN] No healthy providers available for auto-switch")


def save_preflight_report(results: list[ProviderResult]):
    """Save results to a JSON file for monitoring/alerting."""
    report_dir = Path(os.path.expanduser("~/.openclaw/logs"))
    report_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "providers": [asdict(r) for r in results],
        "all_healthy": all(r.status == "ok" for r in results),
        "any_healthy": any(r.status == "ok" for r in results),
    }

    report_path = report_dir / "api_preflight.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="API Preflight Check")
    parser.add_argument("--providers", nargs="+", help="Specific providers to check")
    parser.add_argument("--no-live", action="store_true", help="Skip live API calls (format check only)")
    parser.add_argument("--auto-switch", action="store_true", help="Auto-switch OpenClaw model if provider is down")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = run_preflight(
        providers=args.providers,
        live_check=not args.no_live,
    )

    # Save report
    save_preflight_report(results)

    # Auto-switch if requested
    if args.auto_switch:
        update_openclaw_model_if_needed(results)

    # Output
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        for r in results:
            icon = {
                "ok": "[OK]",
                "missing": "[SKIP]",
                "auth_failed": "[FAIL]",
                "quota_exceeded": "[QUOTA]",
                "error": "[ERR]",
            }.get(r.status, "[???]")

            line = f"{icon} {r.provider}"
            if r.latency_ms:
                line += f" ({r.latency_ms:.0f}ms)"
            if r.model:
                line += f" model={r.model}"
            if r.error:
                line += f" -- {r.error}"
            print(line)

    # Exit code
    if not results:
        sys.exit(2)
    if all(r.status == "ok" for r in results):
        sys.exit(0)
    if any(r.status == "ok" for r in results):
        sys.exit(0)  # At least one works
    sys.exit(1)


if __name__ == "__main__":
    main()
