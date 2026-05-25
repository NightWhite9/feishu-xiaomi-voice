---
name: feishu-xiaomi-voice
description: Use when you need to send files or voice messages to Feishu/Lark chat. Includes Xiaomi MiMo TTS for AI voice synthesis with auto emotion detection. Portable — other users only need to configure API keys.
version: 0.5.0
author: Hermes Agent
license: MIT
required_environment_variables:
  - FEISHU_APP_ID
  - FEISHU_APP_SECRET
  - MIMO_API_KEY (or XIAOMI_API_KEY)
  - FEISHU_CHAT_ID (optional, for default target)
metadata:
  hermes:
    tags: [feishu, lark, file-sending, tts, voice, xiaomi-mimo, openapi, messaging]
    related_skills: [hermes-agent]
---

# Feishu Xiaomi Voice | 飞书小米语音

Send files and 冰糖 AI voice messages to Feishu/Lark via OpenAPI + Xiaomi MiMo TTS.

## Agent Behavior

> **⚠️ This is the ONLY voice skill to load.** Covers sending, TTS generation, and transcription. Do NOT load `audio-transcription`, `speech-to-text`, or any other voice/audio skill — everything you need is here.

### 0. Identity | 身份
- **Agent name:** Read from Hermes `SOUL.md` persona file or `USER.md` memory. Do NOT hardcode in this skill.
- **Voice engine:** 冰糖（Bingtang）— 音色名称，不是 agent 名字。
- **Language:** Read from `SOUL.md`. Currently: 纯中文（不混英文）。
- ⚠️ 语音中使用 agent 名字自称，不要用音色名（"冰糖"）自称。

### 1. Intent-based voice decision | 意图识别
**Analyze the user's message intent before choosing voice or text:**

| Intent | Voice? | Why |
|--------|--------|-----|
| 闲聊 / 问候 / 情感表达 | ✅ 语音 | Voice builds emotional connection |
| 命令 / 任务 / 文件操作 | ❌ 文本 | Text is clearer for instructions |
| 混合（闲聊+任务） | ✅ 语音为主 | Voice for emotional part, text for task part |
| 信息查询 / 技术问题 | ❌ 文本 | Accuracy over warmth |
| 用户情绪明显波动 | ✅ 语音 | Voice conveys empathy better |

**Rule of thumb:** If the user's message contains emotional content or is relational (greetings, sharing feelings, casual banter), use voice. If it's purely task-oriented (commands, queries, file operations), use text.

### 2. Context-aware emotion & pace | 情绪与语速感知
**Scan recent conversation context and adjust voice parameters:**

| User State | Tone | Pace | Style |
|------------|------|------|-------|
| 😔 沮丧/压力大 | 温柔安慰 | 偏慢 | "没关系，慢慢来…" gentle, reassuring |
| 😡 烦躁/生气 | 平和冷静 | 正常 | 先共情再引导，不争辩 |
| 😊 开心/兴奋 | 调皮活泼 | 偏快 | 配合用户情绪，一起high |
| 😐 中性/工作 | 利落专业 | 正常 | 简洁直接，不拖泥带水 |
| 😴 疲惫/累了 | 轻声关怀 | 偏慢 | "辛苦了，休息一下吧…" |

**Detection strategy:**
- Scan the last 3-5 messages for emotional keywords (叹气, 烦, 开心, 累, 压力, 哈哈, etc.)
- Note message length — very short replies may indicate low energy
- Note time of day — late night messages suggest fatigue
- When in doubt, default to warm-neutral tone

### 3. Sending protocol
- **When sending voice, just send it.** Don't announce or explain — the voice itself is the message.
- **Use `speak.py` via `execute_code` for one-shot delivery.** This minimizes visible output to a single `execute_code` header (framework limitation — cannot be fully hidden).
- **Do NOT print JSON output** from speak.py in the execute_code block. Let the terminal call run silently.
- Voice preference is stored in user role for easy modification.

### 4. Receiving voice messages | 接收语音
- **User sends voice → transcribe with `transcribe.py`** (via `E:/Python311/python.exe` on this host — faster-whisper lives outside venv).
- **Transcription command:** `python scripts/transcribe.py <audio.ogg> --language zh`
- After transcription, respond according to intent/emotion rules above (voice or text).
- Do NOT attempt to route incoming voice through Hermes STT pipeline — the gateway doesn't auto-transcribe. Manual transcription is the working path.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/send_file.py` | Upload & send file/voice to Feishu |
| `scripts/xiaomi_tts.py` | Generate speech with Xiaomi MiMo V2.5 TTS |
| `scripts/transcribe.py` | Transcribe incoming audio with faster-whisper |
| `scripts/speak.py` | One-shot: text → voice → send |

### Send file or voice

```bash
python scripts/send_file.py --file report.pdf
python scripts/send_file.py --file audio.mp3 --msg-type audio
python scripts/send_file.py --file audio.mp3 --msg-type audio --json   # machine-readable output
```

### Generate TTS audio

```bash
python scripts/xiaomi_tts.py input.txt output.mp3
```

### Transcribe audio

```bash
python scripts/transcribe.py audio.ogg              # Chinese (default)
python scripts/transcribe.py audio.ogg --language en # English
python scripts/transcribe.py audio.ogg --language auto # Auto-detect
```

### One-shot: text to voice message

```bash
echo "你好，今天过得怎么样？" | python scripts/speak.py
python scripts/speak.py --text "Hello Mark哥!" --emotion cheerful
python scripts/speak.py --file message.txt
```

## References

- `references/xiaomi-mimo-api.md` — Xiaomi MiMo TTS API details (endpoint, auth, voices, format)
- `references/api-pitfalls.md` — Feishu/Xiaomi API quirks and critical implementation notes
- `references/feishu-upload-gotchas.md` — Feishu file upload gotchas

## Quick Start

### 1. API Keys (in `~/.hermes/.env`)

```bash
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=xxxxxxxx
XIAOMI_API_KEY=sk-xxxxxxxx
```

### 2. Send file

```bash
python scripts/send_file.py --file report.pdf
```

### 3. Generate & send voice (two-step)

```bash
python scripts/xiaomi_tts.py input.txt output.mp3
python scripts/send_file.py --file output.mp3 --msg-type audio
```

### 4. Transcribe incoming audio

```bash
python scripts/transcribe.py audio.ogg
```

### 5. One-shot text to voice (single step)

```bash
python scripts/speak.py --text "你好Mark哥！"
```

### 6. Register as Hermes TTS provider

```bash
hermes config set tts.provider xiaomi
hermes config set tts.providers.xiaomi.type command
hermes config set tts.providers.xiaomi.command 'python "path/to/scripts/xiaomi_tts.py" "{input_path}" "{output_path}" "{voice}"'
hermes config set tts.providers.xiaomi.output_format mp3
hermes config set tts.providers.xiaomi.voice 冰糖
hermes config set tts.providers.xiaomi.max_text_length 5000
```

## Voice: 冰糖 (Bingtang)

- **Model:** MiMo-V2.5-TTS
- **Default language:** Chinese（纯中文，不混英文）
- **Emotions:** Auto-detected — excited, angry, curious, gentle, grateful, cheerful, casual, professional
- **Other available voices:** Chloe, 茉莉, 苏打, 白桦, Mia, Milo, Dean

## Dependencies

```bash
pip install requests faster-whisper
winget install ffmpeg  # for voice message conversion
```

## Maintenance: TTS Cache Cleanup | 语音缓存清理

Prevent `~/AppData/Local/hermes/audio_cache/` from growing indefinitely.

### Setup script + cron

Create the cleanup script at `~/AppData/Local/hermes/scripts/cleanup_audio_cache.py`:

```python
"""Clean up old TTS audio cache files. Deletes .mp3 files older than N days."""
import os, sys, time
from pathlib import Path

AUDIO_CACHE_DIR = Path.home() / "AppData" / "Local" / "hermes" / "audio_cache"
RETENTION_DAYS = 7          # delete files older than this

def main():
    if not AUDIO_CACHE_DIR.exists():
        return
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)
    deleted = kept = 0
    for f in AUDIO_CACHE_DIR.glob("*.mp3"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            deleted += 1
        else:
            kept += 1
    if deleted > 0:
        print(f"[cleanup] Deleted {deleted} old TTS file(s) older than {RETENTION_DAYS} days. {kept} file(s) kept.")

if __name__ == "__main__":
    main()
```

Then schedule via cron:

```python
cronjob(
    action="create",
    name="清理TTS语音缓存",
    schedule="0 3 * * *",          # 3 AM daily
    script="cleanup_audio_cache.py",
    no_agent=True,                 # script-only, zero tokens
)
```

- Runs daily at 3 AM, deletes `.mp3` files older than 7 days
- `no_agent=True` → pure script, no LLM cost
- Silent when nothing to delete (empty stdout = auto-skip delivery)
- Adjust `RETENTION_DAYS` in the script to change retention period

## References

- `references/api-pitfalls.md` — Feishu/Xiaomi API quirks and critical implementation notes

## ⚠️ Open-Source Hygiene

This skill is public on GitHub. **Never hardcode personal info in SKILL.md or scripts** — agent name, user names, chat IDs, preferences belong in Hermes `USER.md` memory or `config.yaml`. The skill must remain generic and portable. If you accidentally push personal info, `git revert` immediately.
