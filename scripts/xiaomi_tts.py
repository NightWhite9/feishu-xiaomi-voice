#!/usr/bin/env python3
"""
Xiaomi MiMo TTS v2.5 — Calls chat/completions API with audio output.
Reads text from {input_path}, saves decoded audio to {output_path}.

  POST https://api.xiaomimimo.com/v1/chat/completions
  Header: api-key: <key>
  Body: { model, messages: [{role:user, content: <emotion/style>}, {role:assistant, content: <text>}], audio: {voice, format} }
  Response: choices[0].message.audio.data (base64 WAV/PCM/mp3)

Env vars:
  MIMO_API_KEY        — API key (used as api-key header)
  XIAOMI_TTS_VOICE    — voice ID (default: Chloe, English female)
  XIAOMI_TTS_STYLE    — style/emotion instruction in user message (default: natural friendly tone)
  XIAOMI_TTS_FORMAT   — audio format (default: mp3; also: wav, pcm16)

Pre-built voices:
  Chinese: 冰糖, 茉莉, 苏打, 白桦
  English: Mia, Chloe, Milo, Dean
  Default: mimo_default
"""

import base64
import json
import os
import sys
from pathlib import Path

import requests

def _load_api_key() -> str:
    """Load API key. Always prefer .env file (most up-to-date)."""
    _env_path = Path(os.environ.get("HERMES_HOME", Path.home() / "AppData/Local/hermes")) / ".env"
    # 1. MIMO_API_KEY from .env file (freshest)
    if _env_path.exists():
        for line in _env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("MIMO_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    # 2. MIMO_API_KEY from env
    key = os.environ.get("MIMO_API_KEY", "")
    if key:
        return key
    # 3. XIAOMI_API_KEY from .env file
    if _env_path.exists():
        for line in _env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("XIAOMI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    # 4. XIAOMI_API_KEY from env (last resort)
    return os.environ.get("XIAOMI_API_KEY", "")

API_KEY = _load_api_key()
BASE_URL = "https://api.xiaomimimo.com/v1"
VOICE = os.environ.get("XIAOMI_TTS_VOICE", "")  # User must configure their preferred voice
STYLE = os.environ.get("XIAOMI_TTS_STYLE", "")
FORMAT = os.environ.get("XIAOMI_TTS_FORMAT", "mp3")


def _infer_style(text: str) -> str:
    """Infer a natural speaking style from text content. Like a director giving notes to a voice actor."""
    text_lower = text.lower()

    # Detect language: more CJK characters = Chinese
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    is_chinese = cjk_count > len(text) * 0.3

    # Emotion cues from content
    if any(w in text_lower for w in ['!', 'amazing', 'great', 'awesome', 'congratulations', '恭喜', '太棒', '厉害', 'wow']):
        base = "Excited, upbeat, faster pace, rising pitch at the end. Like you just got amazing news."
    elif any(w in text_lower for w in ['angry', 'mad', 'furious', 'kidding me', 'ridiculous', 'ugh', 'stupid', 'what the', 'seriously', '生气', '气死', '可恶', '离谱', '无语']):
        base = "Annoyed, frustrated, sharp tone. Faster clipped pace. Like you're venting about something that's been driving you crazy."
    elif any(w in text_lower for w in ['?', 'what', 'why', 'how', 'wonder', 'curious', '好奇']):
        base = "Curious, thoughtful tone, slightly slower pace. Like you're pondering an interesting question."
    elif any(w in text_lower for w in ['sorry', 'unfortunately', 'sad', 'bad', 'failed', '抱歉', '遗憾', '可惜']):
        base = "Gentle, empathetic, warm but subdued. Slower pace, soft tone."
    elif any(w in text_lower for w in ['thank', 'thanks', 'appreciate', '谢谢', '感谢']):
        base = "Warm, grateful, sincere. Natural pace with genuine appreciation in the voice."
    elif any(w in text_lower for w in ['hey', 'hi', 'hello', 'morning', '你好', '早上好', 'hi there']):
        base = "Bright, cheerful, energetic. Like greeting a good friend on a sunny morning."
    elif len(text) < 60:
        base = "Casual, relaxed, conversational. Like chatting with a close friend."
    elif any(w in text_lower for w in ['remember', 'note', 'important', 'please', '记住', '注意', '重要']):
        base = "Clear, professional, measured pace. Important information delivered with clarity."
    else:
        base = "Natural, conversational, warm and engaging. Like talking to a trusted colleague."

    # Language: auto-detect, no default preference
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if cjk_count > len(text) * 0.3:
        base += " Speak naturally in Chinese with proper tones."
    elif any(c.isascii() and c.isalpha() for c in text):
        base += " Speak in natural English with a warm accent."

    return base


def main():
    if len(sys.argv) < 3:
        print("Usage: xiaomi_tts.py <input_text_file> <output_audio_file> [voice] [style]", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    voice = sys.argv[3] if len(sys.argv) > 3 else VOICE
    style = sys.argv[4] if len(sys.argv) > 4 else STYLE

    if not API_KEY:
        print("MIMO_API_KEY or XIAOMI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8").strip()
    if not text:
        print("Empty input text", file=sys.stderr)
        sys.exit(1)

    if len(text) > 4000:
        text = text[:4000]

    # Auto-infer style if none provided
    if not style:
        style = _infer_style(text)
        print(f"🎭 Style: {style[:80]}...", file=sys.stderr)

    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "model": "mimo-v2.5-tts",
        "messages": [
            {"role": "user", "content": style},
            {"role": "assistant", "content": text},
        ],
        "audio": {
            "voice": voice,
            "format": FORMAT,
        },
    }

    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json=body,
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"API error {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    try:
        audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    except (KeyError, IndexError, TypeError) as e:
        print(f"Unexpected response structure: {json.dumps(data, ensure_ascii=False)[:500]}", file=sys.stderr)
        sys.exit(1)

    audio_bytes = base64.b64decode(audio_b64)
    output_path.write_bytes(audio_bytes)
    print(f"Generated {len(audio_bytes)} bytes → {output_path}")


if __name__ == "__main__":
    main()
