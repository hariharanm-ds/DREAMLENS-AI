@echo off
REM DreamLens AI - Start Flask app with Groq

echo ================================================================
echo   DREAMLENS AI - Starting Flask App
echo   Powered by Groq
echo ================================================================

if "%GROQ_API_KEY%"=="" (
    echo.
    echo   WARNING: GROQ_API_KEY is not set.
    echo   Set it before using model interpretation.
    echo.
)

cd /d "E:\DreamLensAI"
python app.py

pause
