@echo off
REM DreamLens AI - Start Everything Script

echo ================================================================
echo DREAMLENS AI - Starting All Services
echo ================================================================

REM Get the Ollama path
set "OLLAMA_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe"

REM Check if Ollama exists
if not exist "%OLLAMA_PATH%" (
    echo ERROR: Ollama not found at %OLLAMA_PATH%
    echo Please install Ollama from https://ollama.ai
    pause
    exit /b 1
)

echo.
echo Step 1: Checking if Mistral model is downloaded...
echo This will take a moment...
echo.

REM Start Ollama server in background
echo Starting Ollama server...
start "Ollama Server" "%OLLAMA_PATH%" serve

REM Wait for server to start
timeout /t 5 /nobreak

echo.
echo Step 2: Flask server starting...
echo.

cd /d "E:\DreamLensAI\DREAMLENS AI"

REM Start Flask app
echo Starting DreamLens AI Flask app...
python app_llm.py

pause
