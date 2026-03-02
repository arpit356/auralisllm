@echo off
SETLOCAL EnableDelayedExpansion

echo ---------------------------------------
echo   Auralis AI - Robust Startup System
echo ---------------------------------------

:: 1. Cleanup Port 8000
echo [*] Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo [!] Found blocking process (PID: %%a). Terminating...
    taskkill /F /PID %%a >nul 2>&1
)

:: 2. Check if Ollama is running
echo [*] Checking for Ollama engine...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama is running.
) else (
    echo [!] Ollama is NOT running! 
    echo [!] Please open the Ollama app from your Start Menu.
    pause
    exit /b
)

:: 3. Installing dependencies (silently check)
echo [*] Verifying dependencies...
pip install -r requirements.txt --quiet

:: 4. Start Auralis
echo ---------------------------------------
echo [SUCCESS] Starting Auralis API...
echo ---------------------------------------
python auralis_api.py
pause
