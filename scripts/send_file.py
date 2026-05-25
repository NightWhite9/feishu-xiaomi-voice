#!/usr/bin/env python3
"""
Feishu File Sender — Upload a local file to Feishu and send as file or voice message.
Uses Feishu OpenAPI (tenant_access_token → upload → send).

Config:
  FEISHU_APP_ID       — from open.feishu.cn
  FEISHU_APP_SECRET   — from open.feishu.cn
  FEISHU_CHAT_ID      — default receive_id (chat_id), e.g. oc_xxx

Usage:
  # Send as file
  python send_file.py --file /path/to/report.pdf
  # Send as voice message (auto-converts to opus)
  python send_file.py --file /path/to/audio.mp3 --msg-type audio
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────
APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")

if not APP_ID or not APP_SECRET:
    raise RuntimeError(
        "FEISHU_APP_ID and FEISHU_APP_SECRET must be set in environment "
        "or ~/.hermes/.env. Get them from https://open.feishu.cn/app"
    )

BASE = "https://open.feishu.cn/open-apis"

# Cache token in memory (module-level, lasts process lifetime)
_token_cache = {"token": None, "expires_at": 0}


def get_tenant_access_token() -> str:
    """Get a tenant_access_token, with in-process caching."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    url = f"{BASE}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=15)
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Failed to get tenant_access_token: {resp.text}")

    _token_cache["token"] = data["tenant_access_token"]
    _token_cache["expires_at"] = now + data.get("expire", 7200)
    return _token_cache["token"]


def upload_file(file_path: str, file_type: str | None = None) -> dict:
    """Upload a file to Feishu. Returns {"file_key": "..."} on success."""
    token = get_tenant_access_token()
    url = f"{BASE}/im/v1/files"

    file_path = Path(file_path).resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    ft = file_type or _guess_file_type(file_path)

    with open(file_path, "rb") as f:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            data={
                "file_type": ft,
                "file_name": file_path.name,
            },
            files={"file": (file_path.name, f)},
            timeout=120,
        )

    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Upload failed: {resp.text}")

    return {"file_key": data["data"]["file_key"]}


def send_file_message(file_key: str, receive_id: str,
                      receive_id_type: str = "chat_id",
                      msg_type: str = "file") -> dict:
    """Send a file/audio message to a Feishu chat/user."""
    token = get_tenant_access_token()
    url = f"{BASE}/im/v1/messages?receive_id_type={receive_id_type}"

    body = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": json.dumps({"file_key": file_key}),
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30,
    )

    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Send message failed: {resp.text}")

    return data.get("data", {})


def _find_ffmpeg() -> str:
    """Find ffmpeg executable at common locations."""
    import shutil
    # Check PATH first
    found = shutil.which("ffmpeg")
    if found:
        return found
    # Check common winget install location
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages",
        Path("C:/Users") / os.environ.get("USERNAME", "") / "AppData/Local/Microsoft/WinGet/Packages",
    ]
    for base in candidates:
        if base.exists():
            for d in base.iterdir():
                if d.is_dir() and "FFmpeg" in d.name:
                    for exe in d.rglob("ffmpeg.exe"):
                        return str(exe)
    raise RuntimeError("ffmpeg not found. Install: winget install ffmpeg")


def convert_to_opus(input_path: Path) -> Path:
    """Convert audio to opus format using ffmpeg. Returns path to opus file."""
    if input_path.suffix.lower() == ".opus":
        return input_path

    ffmpeg_bin = _find_ffmpeg()
    output_path = input_path.with_suffix(".opus")
    print(f"🔄 Converting to opus: {input_path.name} → {output_path.name}", file=sys.stderr)

    result = subprocess.run(
        [ffmpeg_bin, "-y", "-i", str(input_path),
         "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", "-ac", "1",
         str(output_path)],
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")

    return output_path


def _guess_file_type(path: Path) -> str:
    """Guess the Feishu file_type from extension."""
    ext = path.suffix.lower()
    mapping = {
        ".pdf": "pdf",
        ".doc": "doc",
        ".docx": "docx",
        ".xls": "xls",
        ".xlsx": "xlsx",
        ".ppt": "pptx",
        ".pptx": "pptx",
        ".csv": "stream",
        ".txt": "stream",
        ".zip": "stream",
        ".rar": "rar",
        ".7z": "7z",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".gif": "image",
        ".webp": "image",
        ".mp3": "mp3",
        ".mp4": "mp4",
        ".wav": "wav",
        ".ogg": "ogg",
        ".opus": "opus",
    }
    return mapping.get(ext, "stream")


def resolve_receive_id(explicit: str | None) -> str:
    """Resolve receive_id: explicit arg → env vars → error if unset."""
    if explicit:
        return explicit
    for var in ("FEISHU_CHAT_ID", "FEISHU_RECEIVE_ID", "HERMES_FEISHU_CHAT"):
        val = os.environ.get(var)
        if val:
            return val
    raise RuntimeError(
        "No receive_id provided. Set FEISHU_CHAT_ID in .env or pass --receive-id"
    )


def main():
    parser = argparse.ArgumentParser(description="Send a file or voice message to Feishu")
    parser.add_argument("--file", required=True, help="Local file path")
    parser.add_argument("--receive-id", default=None, help="chat_id or open_id")
    parser.add_argument("--receive-id-type", default="chat_id",
                        choices=["chat_id", "open_id", "user_id"])
    parser.add_argument("--msg-type", default="file", choices=["file", "audio"],
                        help="Message type: file (default) or audio (voice message)")
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Output machine-readable JSON instead of human text")
    args = parser.parse_args()

    receive_id = resolve_receive_id(args.receive_id)
    file_path = Path(args.file).resolve()

    # For audio messages, convert to opus if needed
    upload_path = file_path
    upload_file_type = None
    if args.msg_type == "audio":
        upload_path = convert_to_opus(file_path)
        upload_file_type = "opus"

    _log(args, f"Uploading: {upload_path}")
    result = upload_file(str(upload_path), file_type=upload_file_type)
    file_key = result["file_key"]
    _log(args, f"Uploaded — file_key: {file_key}")

    _log(args, f"Sending to: {receive_id} (type: {args.msg_type})")
    msg = send_file_message(file_key, receive_id, args.receive_id_type, msg_type=args.msg_type)
    message_id = msg.get("message_id", "N/A")
    _log(args, f"Sent — message_id: {message_id}")

    # Clean up converted opus file
    if upload_path != file_path and upload_path.exists():
        upload_path.unlink()

    if args.json_output:
        print(json.dumps({
            "file_key": file_key,
            "message_id": message_id,
            "receive_id": receive_id,
            "msg_type": args.msg_type,
        }))

    return 0


def _log(args, msg: str) -> None:
    """Log to stderr if not in JSON mode."""
    if not args.json_output:
        print(msg, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
