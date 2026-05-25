#!/usr/bin/env python3
"""Transcribe audio files using faster-whisper.
Usage: python transcribe.py <audio_file> [--language zh|en|auto]
"""
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with faster-whisper")
    parser.add_argument("file", help="Path to audio file (.ogg, .mp3, .wav, etc.)")
    parser.add_argument("--language", default="zh", choices=["zh", "en", "auto"],
                        help="Language (default: zh, auto for detection)")
    parser.add_argument("--model", default="small", choices=["tiny", "small", "medium"],
                        help="Whisper model size (default: small)")
    args = parser.parse_args()

    audio_path = os.path.abspath(args.file)
    if not os.path.exists(audio_path):
        print(f"❌ File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    from faster_whisper import WhisperModel

    lang = None if args.language == "auto" else args.language
    device = "cpu"
    compute = "int8"

    print(f"🎙️ Loading model '{args.model}'...", file=sys.stderr)
    model = WhisperModel(args.model, device=device, compute_type=compute)

    print(f"📝 Transcribing: {os.path.basename(audio_path)}", file=sys.stderr)
    segments, info = model.transcribe(audio_path, language=lang)

    print(f"🌐 Language: {info.language} ({info.language_probability:.0%})", file=sys.stderr)
    print("---")

    for segment in segments:
        print(f"[{segment.start:.1f}s] {segment.text.strip()}")

if __name__ == "__main__":
    main()
