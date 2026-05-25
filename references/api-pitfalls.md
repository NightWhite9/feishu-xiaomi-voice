# Feishu & Xiaomi MiMo API Pitfalls

Critical technical details discovered during implementation. Read before modifying the scripts.

## Feishu OpenAPI: File Upload

### file_type / file_name must be `data`, not `files`

The Feishu `/im/v1/files` endpoint requires `file_type` and `file_name` as multipart form fields (`data` in requests), NOT as file tuples. Sending them via `files={...}` causes error 234001 ("Invalid request param").

**Correct:**
```python
requests.post(url,
    data={"file_type": "stream", "file_name": "test.txt"},
    files={"file": ("test.txt", file_obj)},
)
```

**Wrong:**
```python
requests.post(url,
    files={
        "file_type": (None, "stream"),
        "file_name": (None, "test.txt"),
        "file": ("test.txt", file_obj),
    },
)
```

### File type mapping: only specific values accepted

Feishu only accepts certain `file_type` values: `opus, mp4, pdf, doc, docx, xls, xlsx, ppt, pptx, stream, image, rar, 7z`. Use `stream` for txt/csv/zip/generic binaries. `image` for png/jpg/gif/webp.

### Voice messages require Opus format

Feishu voice messages (`msg_type: audio`) require the uploaded file to be `file_type: opus`. Non-opus audio must be converted first via ffmpeg.

## Xiaomi MiMo TTS API

### Endpoint is chat/completions, NOT audio/speech

Xiaomi MiMo V2.5 TTS uses `POST /v1/chat/completions` with `audio` parameter — NOT a dedicated TTS endpoint. Model: `mimo-v2.5-tts`.

### Auth header: `api-key`, NOT `Authorization: Bearer`

```python
headers = {"api-key": API_KEY}  # Correct
# headers = {"Authorization": f"Bearer {API_KEY}"}  # Wrong — 401
```

### Text placement: assistant role, NOT user

The text to speak goes in `messages[1].role: "assistant"`. Style/emotion instructions go in `messages[0].role: "user"`.

### Platform key vs Token Plan key

- Platform API key (`sk-...`) — works with `api.xiaomimimo.com` ✅
- Token Plan key (`tp-...`) — works with `token-plan-cn.xiaomimimo.com` ❌ for TTS

Get platform key from https://platform.xiaomimimo.com (not from Token Plan console).

### Available voices

| Chinese | English |
|---------|---------|
| 冰糖, 茉莉, 苏打, 白桦 | Chloe, Mia, Milo, Dean |

### Emotion control via natural language

The `user` message content is the style instruction. Natural language works best:
- "Excited, upbeat, faster pace"
- "Annoyed, frustrated, sharp tone"
- "Gentle, empathetic, slower pace"

## Agent Identity Pitfall

The voice name (冰糖/Chloe/etc.) is the TTS **engine**, NOT the agent's identity. When generating voice content, use the agent's actual name (typically set by the user — e.g. "小乖"), never default to the voice engine name. Saying "冰糖随时待命" is wrong — the engine doesn't have agency. Say "小乖随时待命" instead.

## Environment Variable Staleness

Hermes TTS command providers run in a subprocess. The parent process's env vars may be stale (loaded at startup). Scripts should read `.env` file directly as a fallback, which is always current.
