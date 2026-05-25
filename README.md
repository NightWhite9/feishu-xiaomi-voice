# feishu-xiaomi-voice

> 飞书智能语音助手 — 冰糖 AI 语音 + 飞书文件发送，一站式语音技能包

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.5.0-blue)](SKILL.md)

## ✨ 功能

| 功能 | 脚本 | 说明 |
|------|------|------|
| 🚀 一键语音 | `speak.py` | 文字 → 冰糖语音 → 飞书，一步到位 |
| 🎙️ 文字转语音 | `xiaomi_tts.py` | 小米 MiMo V2.5 TTS，自动情绪检测 |
| 📝 语音转文字 | `transcribe.py` | faster-whisper 转录，支持中英文 |
| 📤 发送文件 | `send_file.py` | 上传文件到飞书，支持文件 & 语音消息 |

> ⚠️ **MiMo V2.5 TTS 限时免费中**，后续收费以[官方](https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5)为准。

## 🔗 脚本调用链

```
speak.py ──────────────────── 一键方案（推荐）
  ├── xiaomi_tts.py ──→ 生成 mp3
  └── send_file.py ──→ 发送到飞书

文字 ──→ xiaomi_tts.py ──→ mp3 ──→ send_file.py --msg-type audio ──→ 飞书  （分步）

语音消息 ──→ transcribe.py ──→ 文字 ──→ 理解 ──→ 走上面发语音回复
```

## 🎭 智能语音行为

- **意图识别**：闲聊/情感 → 语音；任务/查询 → 文字
- **情绪感知**：根据上下文自动调整语气和语速
  - 😔 沮丧 → 温柔安慰、慢语速
  - 😊 开心 → 调皮活泼、快语速
  - 😡 烦躁 → 平和冷静
  - 😴 疲惫 → 轻声关怀

## 🚀 快速开始

### 0. 安装

```bash
npx skills add NightWhite9/feishu-xiaomi-voice
```

安装后脚本在 `skills/feishu-xiaomi-voice/scripts/` 目录下。

### 1. 配置 API 密钥

```bash
export FEISHU_APP_ID=cli_xxxxxxxx
export FEISHU_APP_SECRET=xxxxxxxx
export MIMO_API_KEY=sk-xxxxxxxx
export FEISHU_CHAT_ID=oc_xxxxxxxx    # 可选，默认发送目标
```

获取方式：
- **飞书**：[open.feishu.cn](https://open.feishu.cn) → 创建应用 → 凭证与基础信息
- **小米 MiMo TTS**：[platform.xiaomimimo.com](https://platform.xiaomimimo.com) → API Keys

### 2. 开始使用

```bash
# 一键发送语音
python scripts/speak.py --text "你好，今天过得怎么样？"

# 分步操作
python scripts/xiaomi_tts.py input.txt output.mp3
python scripts/send_file.py --file output.mp3 --msg-type audio

# 转录收到的语音
python scripts/transcribe.py audio.ogg
```

## 🎤 音色

默认音色：**冰糖**（中文女声）

| 中文 | 英文 |
|------|------|
| 冰糖、茉莉、苏打、白桦 | Chloe、Mia、Milo、Dean |

切换音色：
```bash
# 单次调用
python scripts/speak.py --text "..." --voice 茉莉

# 全局切换
hermes config set tts.providers.xiaomi.voice 茉莉
```

## 📁 项目结构

```
.
├── SKILL.md                     # Agent 技能定义（含工作流）
├── README.md
├── LICENSE
├── scripts/
│   ├── speak.py                 # 一键：文字 → 语音 → 飞书
│   ├── send_file.py             # 飞书文件/语音发送
│   ├── xiaomi_tts.py            # MiMo TTS 语音合成
│   └── transcribe.py            # 语音转文字
└── references/
    ├── xiaomi-mimo-api.md       # MiMo API 参考
    ├── api-pitfalls.md          # API 踩坑记录
    └── feishu-upload-gotchas.md # 飞书上传注意事项
```

## 🔒 安全

- 所有凭据通过**环境变量**读取，代码中无硬编码
- API 密钥不会出现在日志或输出中
- `.env` 文件已加入 `.gitignore`
- 个人信息（名字、偏好）不写入公开文件

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)
