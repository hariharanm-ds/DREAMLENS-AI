@echo off
REM DreamLens AI - Start Everything Script (Ollama + Flask)

echo ================================================================
echo   DREAMLENS AI - Starting All Services
echo   Powered by Ollama Llama 3
echo ================================================================

REM --- Step 1: Check if Ollama is installed ---
echo.
echo [Step 1] Checking for Ollama...

where ollama >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   Found Ollama in PATH
    set "OLLAMA_CMD=ollama"
    goto :ollama_found
)

set "OLLAMA_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe"
if exist "%OLLAMA_PATH%" (
    echo   Found Ollama at %OLLAMA_PATH%
    set "OLLAMA_CMD=%OLLAMA_PATH%"
    goto :ollama_found
)

echo   ERROR: Ollama not found!
echo   Please install Ollama from https://ollama.ai
echo   Then run: ollama pull llama3
pause
exit /b 1

:ollama_found

REM --- Step 2: Start Ollama server ---
echo.
echo [Step 2] Starting Ollama server...
start "Ollama Server" "%OLLAMA_CMD%" serve

REM Wait for server to initialize
echo   Waiting for Ollama to start...
timeout /t 5 /nobreak >nul

REM --- Step 3: Check if Llama 3 is available ---
echo.
echo [Step 3] Checking for Llama 3 model...
"%OLLAMA_CMD%" list 2>nul | findstr /i "llama3" >nul
if %ERRORLEVEL% NEQ 0 (
    echo   Llama 3 not found. Pulling now (this may take a few minutes)...
    "%OLLAMA_CMD%" pull llama3
    if %ERRORLEVEL% NEQ 0 (
        echo   WARNING: Failed to pull llama3. The app will run but AI features won't work.
        echo   Try manually: ollama pull llama3
    ) else (
        echo   Llama 3 downloaded successfully!
    )
) else (
    echo   Llama 3 is ready!
)

REM --- Step 4: Start Flask app ---
echo.
echo [Step 4] Starting DreamLens AI Flask app...
echo ================================================================
echo   Open your browser at: http://127.0.0.1:5000
echo ================================================================
echo.

cd /d "E:\DreamLensAI"
python app.py

pause
