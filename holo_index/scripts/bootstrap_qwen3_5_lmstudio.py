#!/usr/bin/env python3
"""
Bootstrap Qwen3.5 4B GGUF for Foundups local runtime.

Default workflow:
1) Download model to E:/HoloIndex/models/qwen3.5-4b
2) Mirror model into LOCAL_MODEL_GENERAL_DIR (or LM Studio local root)
3) Check LM Studio API and request model load
4) Optionally run a smoke chat completion
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from huggingface_hub import hf_hub_download


DEFAULT_REPO_ID = "lmstudio-community/Qwen3.5-4B-GGUF"
DEFAULT_FILENAME = "Qwen3.5-4B-Q4_K_M.gguf"


def _resolve_holo_model_root() -> Path:
    explicit = os.getenv("HOLO_MODEL_ROOT", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    holo_ssd = os.getenv("HOLO_SSD_PATH", "E:/HoloIndex").strip() or "E:/HoloIndex"
    return Path(holo_ssd).expanduser() / "models"


def _resolve_lm_general_dir() -> Path:
    explicit = os.getenv("LOCAL_MODEL_GENERAL_DIR", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    local_root = os.getenv("LOCAL_MODEL_ROOT", "E:/LM_studio/models/local").strip()
    return Path(local_root).expanduser() / "qwen3.5-4b"


def _lm_base_url() -> str:
    port = int(os.getenv("LM_STUDIO_PORT", "1234"))
    return f"http://127.0.0.1:{port}"


def _download_model(repo_id: str, filename: str, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    target = dst_dir / filename
    if target.exists():
        print(f"[OK] Model already present: {target}")
        return target

    print(f"[DOWNLOAD] {repo_id}/{filename}")
    downloaded = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=str(dst_dir),
        local_dir_use_symlinks=False,
    )
    downloaded_path = Path(downloaded)
    print(f"[OK] Downloaded: {downloaded_path}")
    return downloaded_path


def _mirror_into_lmstudio(src_file: Path, lm_dir: Path) -> Path:
    lm_dir.mkdir(parents=True, exist_ok=True)
    dst_file = lm_dir / src_file.name

    if dst_file.exists():
        if dst_file.stat().st_size == src_file.stat().st_size:
            print(f"[OK] LM Studio model already mirrored: {dst_file}")
            return dst_file
        dst_file.unlink()

    try:
        os.link(src_file, dst_file)
        print(f"[OK] Created hardlink for LM Studio: {dst_file}")
        return dst_file
    except OSError:
        shutil.copy2(src_file, dst_file)
        print(f"[OK] Copied model for LM Studio: {dst_file}")
        return dst_file


def _get_models(base_url: str, timeout_s: float = 5.0) -> List[Dict[str, Any]]:
    resp = requests.get(f"{base_url}/v1/models", timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", [])
    return items if isinstance(items, list) else []


def _find_loaded_model(models: List[Dict[str, Any]]) -> Optional[str]:
    for item in models:
        model_id = str(item.get("id", "")).strip()
        if "qwen3.5" in model_id.lower():
            return model_id
    return None


def _request_model_load(base_url: str, model_id: str, filename: str) -> bool:
    endpoints = ("/v1/models/load", "/api/v0/models/load", "/api/models/load")
    payloads = (
        {"model": model_id, "file": filename},
        {"model": model_id},
        {"id": model_id, "file": filename},
    )
    for endpoint in endpoints:
        for payload in payloads:
            try:
                resp = requests.post(f"{base_url}{endpoint}", json=payload, timeout=20)
                if resp.status_code in (200, 201, 202):
                    print(f"[OK] Load request accepted via {endpoint}: {payload}")
                    return True
            except requests.RequestException:
                continue
    return False


def _wait_for_loaded_model(base_url: str, timeout_s: float = 90.0) -> Optional[str]:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            models = _get_models(base_url, timeout_s=5.0)
            loaded = _find_loaded_model(models)
            if loaded:
                return loaded
        except requests.RequestException:
            pass
        time.sleep(2.0)
    return None


def _smoke_chat(base_url: str, model_id: str) -> bool:
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Reply with OK only."}],
        "temperature": 0.0,
        "max_tokens": 8,
    }
    try:
        resp = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        print(f"[SMOKE] Response: {content or '<empty>'}")
        return bool(content)
    except requests.RequestException as exc:
        print(f"[WARN] Smoke test failed: {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Qwen3.5 model for LM Studio.")
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Hugging Face repo id.")
    parser.add_argument("--filename", default=DEFAULT_FILENAME, help="GGUF filename.")
    parser.add_argument(
        "--download-root",
        default=str(_resolve_holo_model_root()),
        help="Root directory for Holo model downloads.",
    )
    parser.add_argument(
        "--folder",
        default="qwen3.5-4b",
        help="Model folder name under --download-root.",
    )
    parser.add_argument(
        "--lm-dir",
        default=str(_resolve_lm_general_dir()),
        help="LM Studio local model directory for mirror/link.",
    )
    parser.add_argument(
        "--model-id",
        default=os.getenv("QWEN35_MODEL_ID", DEFAULT_REPO_ID),
        help="LM Studio model id for /models/load.",
    )
    parser.add_argument("--download-only", action="store_true", help="Only download, skip LM Studio steps.")
    parser.add_argument("--skip-mirror", action="store_true", help="Do not mirror model into LM Studio dir.")
    parser.add_argument("--skip-load", action="store_true", help="Do not request model load in LM Studio.")
    parser.add_argument("--smoke", action="store_true", help="Run chat-completion smoke test after load.")
    args = parser.parse_args()

    download_root = Path(args.download_root).expanduser()
    model_dir = download_root / args.folder
    lm_dir = Path(args.lm_dir).expanduser()
    base_url = _lm_base_url()

    print("=" * 72)
    print("Qwen3.5 Bootstrap")
    print("=" * 72)
    print(f"Download dir: {model_dir}")
    print(f"LM Studio dir: {lm_dir}")
    print(f"LM Studio API: {base_url}")
    print(f"Model id     : {args.model_id}")
    print()

    src_file = _download_model(args.repo_id, args.filename, model_dir)
    if not args.skip_mirror:
        _mirror_into_lmstudio(src_file, lm_dir)

    if args.download_only:
        print("[DONE] Download-only mode complete.")
        return 0

    try:
        models = _get_models(base_url)
        loaded = _find_loaded_model(models)
        if loaded:
            print(f"[OK] LM Studio already has Qwen3.5 loaded: {loaded}")
        elif args.skip_load:
            print("[WARN] Qwen3.5 not loaded and --skip-load was set.")
            return 2
        else:
            accepted = _request_model_load(base_url, args.model_id, args.filename)
            if not accepted:
                print("[WARN] Could not submit model-load request to LM Studio.")
                print("      Open LM Studio and load Qwen3.5 manually from Local Models.")
                return 2
            loaded = _wait_for_loaded_model(base_url, timeout_s=120.0)
            if not loaded:
                print("[WARN] LM Studio did not report Qwen3.5 as loaded within timeout.")
                return 2
            print(f"[OK] LM Studio loaded model: {loaded}")

        if args.smoke and loaded:
            smoke_ok = _smoke_chat(base_url, loaded)
            if not smoke_ok:
                return 3
    except requests.RequestException as exc:
        print(f"[WARN] LM Studio API is unavailable: {type(exc).__name__}: {exc}")
        print("      Start LM Studio and enable the local server first.")
        return 2

    print("[DONE] Qwen3.5 bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
