# Runbook

## Start Backend

Recommended Windows workflow:

```bat
scripts\start-dev.bat
```

This opens separate CMD windows for backend and frontend.

Manual backend command:

```powershell
cd D:\listen_book\backend
..\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```

Health check:

```powershell
curl.exe http://127.0.0.1:8000/api/health
```

## Start Frontend

Manual frontend command:

```powershell
cd D:\listen_book\frontend
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173/
```

## Build And Lint

Frontend build:

```powershell
cd D:\listen_book\frontend
npm run build
```

Backend lint:

```powershell
cd D:\listen_book
.venv\Scripts\ruff.exe check --no-cache backend\app
```

## Stop Dev Services

```bat
scripts\stop-dev.bat
```

## Manual Worker Fallback

Uploads now trigger one background parse job from the API. If a pending parse job needs to be retried manually:

```powershell
cd D:\listen_book
.venv\Scripts\python.exe -m app.workers.parse_books
```

## Local Testing Notes

- `GET /api/books` should return uploaded books.
- `GET /api/books/{book_id}/chapters` should return chapters only after a book reaches `ready`.
- `POST /api/audio/sentences/{sentence_id}` generates or reuses cached sentence audio.
- Vite proxies frontend `/api` calls to `http://localhost:8000`.
- In restricted Codex sessions, Vite may need approval because it starts an `esbuild` child process.
- The first real TTS provider uses `edge-tts`, so audio generation needs network access.
