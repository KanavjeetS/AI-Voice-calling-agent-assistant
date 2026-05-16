#!/bin/bash
set -euo pipefail

echo "Downloading Kokoro TTS model..."
python -c "from kokoro_onnx import Kokoro; Kokoro('kokoro-v1_0.onnx','voices-v1_0.bin')"

echo "Downloading Whisper model (large-v3-turbo)..."
python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"

echo "Downloading embedding model..."
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)"

echo "All models downloaded. Disk usage:"
du -sh ~/.cache/huggingface/
