# Feishu File Upload — Key Gotchas

## Multipart Form Encoding

Feishu `/im/v1/files` expects `file_type` and `file_name` as regular form fields (NOT as file parts):

```python
# ✅ CORRECT
requests.post(url,
    data={
        "file_type": "stream",
        "file_name": "report.txt",
    },
    files={"file": ("report.txt", f)},
)

# ❌ WRONG — causes 234001 "Invalid request param"
requests.post(url,
    files={
        "file_type": (None, "stream"),
        "file_name": (None, "report.txt"),
        "file": ("report.txt", f),
    },
)
```

## File Type Mapping

Use `stream` for generic file types that Feishu doesn't have explicit support for:

| Extension | Feishu file_type |
|-----------|-----------------|
| .txt, .csv, .zip | `stream` |
| .pdf | `pdf` |
| .docx | `docx` |
| .xlsx | `xlsx` |
| .png, .jpg | `image` |
| .mp3 | `mp3` |
| .opus | `opus` |

## Voice Messages

- Upload: `file_type=opus`
- Send: `msg_type=audio`, content: `{"file_key": "..."}`
- Requires ffmpeg to convert to opus format first

## File Size Limit

20 MB per file (Feishu API limit).
