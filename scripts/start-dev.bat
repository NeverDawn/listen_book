@echo off
setlocal

set "ROOT=%~dp0.."
set "BACKEND=%ROOT%\backend"
set "FRONTEND=%ROOT%\frontend"

echo Starting Listen Book backend and frontend...
echo.

start "Listen Book Backend" cmd /k "cd /d "%BACKEND%" && ..\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000"
start "Listen Book Frontend" cmd /k "cd /d "%FRONTEND%" && npm run dev -- --host 127.0.0.1"

echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo.
echo Two command windows were opened. Keep them open while developing.

endlocal
