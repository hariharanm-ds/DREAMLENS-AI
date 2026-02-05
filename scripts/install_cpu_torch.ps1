# PowerShell script to install CPU-only PyTorch on Windows
# Run in an elevated PowerShell or virtual environment where you want to install packages.
# This installs CPU-only wheels which avoid GPU DLL init issues on Windows.

Write-Output "Installing CPU-only PyTorch (stable) via pip..."
python -m pip install --upgrade pip
# CPU-only wheels hosted on pytorch index
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio --extra-index-url https://pypi.org/simple

Write-Output "Installation finished. Check with: python -c "import torch; print(torch.__version__)""