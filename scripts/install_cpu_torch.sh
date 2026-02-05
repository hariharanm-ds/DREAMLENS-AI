#!/usr/bin/env bash
# Install CPU-only PyTorch on Linux/Mac
set -e
python -m pip install --upgrade pip
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio

echo "Installed CPU-only PyTorch. Verify with: python -c 'import torch; print(torch.__version__)'"