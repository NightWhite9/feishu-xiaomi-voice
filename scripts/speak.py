#!/usr/bin/env python3
"""
One-shot: text → 冰糖 voice → Feishu message.
Combines TTS generation + file sending in a single step.

Usage:
  echo "你好！" | python speak.py
  python speak.py --text "Hello Mark哥!"
  python speak.py --file message.txt
  python speak.py --text "好消息！" --emotion cheerful
  python speak.py --text "..." --json   # machine-readable output
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TTS_SCRIPT = SCRIPT_DIR / "xiaomi_tts.py"
SEND_SCRIPT = SCRIPT_DIR / "send_file.py"


def main():
    parser = argparse.ArgumentParser(
        description="Text → 冰糖 voice → Feishu (one-shot)"
    )
    parser.add_argument(
        "--text", default=None,
        help="Text to speak (reads from stdin if omitted and --file not set)"
    )
    parser.add_argument(
        "--file", default=None,
        help="Read text from file instead of --text or stdin"
    )
    parser.add_argument(
        "--emotion", default=None,
        help="Emotion override (e.g. cheerful, gentle, excited, calm)"
    )
    parser.add_argument(
        "--voice", default=None,
        help="Voice override (default: 冰糖)"
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Output JSON instead of human text"
    )
    args = parser.parse_args()

    # Resolve text input
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8").strip()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read().strip()

    if not text:
        print("Error: no text provided", file=sys.stderr)
        sys.exit(1)

    if len(text) > 4000:
        text = text[:4000]

    # Generate TTS audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        mp3_path = Path(tmp.name)

    voice = args.voice or "冰糖"

    _log(args, f"Generating voice ({voice})...")
    tts_cmd = [
        sys.executable, str(TTS_SCRIPT),
        "-", str(mp3_path), voice
    ]
    _log(args, f"Text: {text[:80]}{'...' if len(text) > 80 else ''}")

    # Need to pipe text via stdin since xiaomi_tts.py reads from file
    # Workaround: write text to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as txt_tmp:
        txt_tmp.write(text)
        txt_path = Path(txt_tmp.name)

    tts_cmd = [
        sys.executable, str(TTS_SCRIPT),
        str(txt_path), str(mp3_path), voice
    ]
    if args.emotion:
        tts_cmd.append(args.emotion)

    result = subprocess.run(tts_cmd, capture_output=True, text=True, timeout=120)
    txt_path.unlink()  # Clean up text temp file

    if result.returncode != 0:
        print(f"TTS failed: {result.stderr}", file=sys.stderr)
        mp3_path.unlink()
        sys.exit(1)

    _log(args, f"Audio: {mp3_path.stat().st_size} bytes")

    # Send to Feishu
    send_cmd = [
        sys.executable, str(SEND_SCRIPT),
        "--file", str(mp3_path),
        "--msg-type", "audio",
    ]
    if args.json_output:
        send_cmd.append("--json")

    result = subprocess.run(send_cmd, capture_output=True, text=True, timeout=60)
    mp3_path.unlink()  # Clean up audio

    if result.returncode != 0:
        print(f"Send failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(result.stdout.strip())
    else:
        print(result.stderr.strip())


def _log(args, msg: str) -> None:
    """Log to stderr if not in JSON mode."""
    if not args.json_output:
        print(msg, file=sys.stderr)


if __name__ == "__main__":
    main()
