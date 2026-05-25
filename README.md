# feishu-xiaomi-voice

> 飞书智能语音助手 — 小米 AI 语音 + 飞书文件发送，一站式语音技能包

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

## ✨ 功能

| 功能 | 脚本 | 说明 |
|------|------|------|
| 📤 发送文件/语音 | `send_file.py` | 上传文件到飞书，支持文件 & 语音消息 |
| 🎙️ 文字转语音 | `xiaomi_tts.py` | 小米 MiMo V2.5 TTS，自动情绪检测 |
| 📝 语音转文字 | `transcribe.py` | faster-whisper 转录，支持中英文 |
| 🚀 一键发送 | `speak.py` | 文字 → 冰糖语音 → 飞书，一步到位 |

> ⚠️ **MiMo V2.5 TTS 限时免费中**，后续收费以[官方](https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5)为准。

## 🎭 智能语音行为

- **意图识别**：闲聊/情感 → 语音；任务/查询 → 文字
- **情绪感知**：根据上下文自动调整语气和语速
  - 😔 沮丧 → 温柔安慰
  - 😊 开心 → 调皮活泼
  - 😡 烦躁 → 平和冷静
  - 😴 疲惫 → 轻声关怀

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests faster-whisper
# Windows: winget install ffmpeg
# macOS: brew install ffmpeg
# Linux: apt install ffmpeg
```

### 2. 配置 API 密钥

```bash
export FEISHU_APP_ID=cli_xxxxxxxx
export FEISHU_APP_SECRET=xxxxxxxx
export MIMO_API_KEY=sk-xxxxxxxx
export FEISHU_CHAT_ID=oc_xxxxxxxx    # 可选，默认发送目标
```

获取方式：
- **飞书**：[open.feishu.cn](https://open.feishu.cn) → 创建应用 → 凭证与基础信息
- **小米 MiMo TTS**：[platform.xiaomimimo.com](https://platform.xiaomimimo.com) → API Keys

### 3. 开始使用

```bash
# 一键发送语音
python speak.py --text "你好，今天过得怎么样？"

# 分步操作
python xiaomi_tts.py input.txt output.mp3
python send_file.py --file output.mp3 --msg-type audio

# 转录收到的语音
python transcribe.py audio.ogg
```

## 🎤 音色

默认音色：**冰糖**（中文女声）

| 中文 | 英文 |
|------|------|
| 冰糖、茉莉、苏打、白桦 | Chloe、Mia、Milo、Dean |

## 🧹 缓存清理

语音缓存目录 (`audio_cache/`) 会随着使用自动增长。设置定时清理任务防止磁盘占用：

```bash
# 创建清理脚本（删除 7 天前的 .mp3 文件）
cat > ~/AppData/Local/hermes/scripts/cleanup_audio_cache.py << 'EOF'
"""Clean up old TTS audio cache files."""
from pathlib import Path
import time

CACHE = Path.home() / "AppData/Local/hermes/audio_cache"
RETENTION = 7 * 86400  # 保留天数（秒）

def main():
    if not CACHE.exists(): return
    now = time.time()
    d = k = 0
    for f in CACHE.glob("*.mp3"):
        if now - f.stat().st_mtime > RETENTION:
            f.unlink(); d += 1
        else: k += 1
    if d: print(f"Deleted {d} file(s), {k} kept.")

if __name__ == "__main__":
    main()
EOF

# 添加到 Hermes cron（每天凌晨 3 点自动运行）
hermes cron add \
  --name "清理TTS语音缓存" \
  --schedule "0 3 * * *" \
  --script cleanup_audio_cache.py \
  --no-agent
```

特点：
- 🕒 每天凌晨 3 点自动执行
- 🔇 无过期文件时完全静默（不打扰）
- ⚡ `--no-agent` 模式，纯脚本运行，零 token 消耗
- ⚙️ 修改脚本中的 `RETENTION` 变量即可调整保留天数

## 📁 项目结构

```
.
├── SKILL.md              # Hermes Agent 技能定义
├── README.md
├── LICENSE
├── scripts/
│   ├── send_file.py      # 飞书文件发送
│   ├── xiaomi_tts.py     # MiMo TTS 语音合成
│   ├── transcribe.py     # 语音转文字
│   └── speak.py          # 一键发送
└── references/
    ├── xiaomi-mimo-api.md      # MiMo API 参考
    ├── api-pitfalls.md         # API 踩坑记录
    └── feishu-upload-gotchas.md # 飞书上传注意事项
```

## 🔒 安全

- 所有凭据通过**环境变量**读取，代码中无硬编码
- API 密钥不会出现在日志或输出中
- `.env` 文件已加入 `.gitignore`

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)
