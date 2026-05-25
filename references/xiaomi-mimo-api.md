# Xiaomi MiMo TTS API Reference

## Endpoint

```
POST https://api.xiaomimimo.com/v1/chat/completions
```

NOT `/v1/audio/speech` (OpenAI-compatible endpoint does not exist).

## Authentication

```http
api-key: sk-xxxxxxxx
```

**CRITICAL:** Uses `api-key` header, NOT `Authorization: Bearer`.

## API Key Types

| Type | Prefix | Domain | TTS Support |
|------|--------|--------|-------------|
| Platform API Key | `sk-...` | `api.xiaomimimo.com` | ✅ Yes |
| Token Plan Key | `tp-...` | `token-plan-cn.xiaomimimo.com` | ❌ No |

Get platform key from: https://platform.xiaomimimo.com

## Request Format

```json
{
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "user", "content": "<style/emotion instruction>"},
        {"role": "assistant", "content": "<text to speak>"}
    ],
    "audio": {
        "voice": "Chloe",
        "format": "mp3"
    }
}
```

- `user` message: style/emotion guidance (natural language)
- `assistant` message: actual text to synthesize
- NOT the other way around!

## Response Format

```json
{
    "choices": [{
        "message": {
            "audio": {
                "data": "<base64 encoded audio>"
            }
        }
    }]
}
```

Audio is base64-encoded in `choices[0].message.audio.data`.

## Supported Formats

- `mp3` (default for script)
- `wav`
- `pcm16` (for streaming, not yet supported by MiMo)

## Pre-built Voices

| Voice | Language | Gender |
|-------|----------|--------|
| 冰糖 | Chinese | Female |
| 茉莉 | Chinese | Female |
| 苏打 | Chinese | Male |
| 白桦 | Chinese | Male |
| Chloe | English | Female |
| Mia | English | Female |
| Milo | English | Male |
| Dean | English | Male |
| mimo_default | Auto | Varies by cluster |

## Style Control

Two methods (both supported by the script):

1. **Natural language** — put in `user` message content
2. **Audio tags** — embed `(style)` or `[tag]` in `assistant` message text

Supported styles: 开心/悲伤/愤怒/温柔/慵懒/俏皮/etc.
Audio tags: (紧张), [笑声], (语速加快), etc.

## Character Limit

~4000 chars practical limit. Longer text should be truncated.

## Pricing & Rate Limits

⚠️ **限时免费中** — MiMo V2.5 TTS 当前免费，后续收费以官方为准。

See: https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5
