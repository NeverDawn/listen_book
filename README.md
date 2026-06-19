# Listen Book

家庭读书/听书 Web 应用。技术栈：

- Backend: Python FastAPI
- Frontend: React + TypeScript
- Database: PostgreSQL
- Storage: local filesystem

当前阶段先搭工程闭环：上传、解析、断句、阅读、朗读接口、音频缓存和进度保存。

## Development

PostgreSQL 已检测到本机安装了 18.x。先创建 `.env`：

```powershell
Copy-Item .env.example .env
```

后续需要创建 `listen_book` 数据库和 `listen_book_app` 用户，或把 `.env` 改成你本机已有账号。

## Backend

虚拟环境位于项目根目录：

```powershell
.venv\Scripts\python.exe
```

依赖安装：

```powershell
.venv\Scripts\python.exe -m pip install --no-cache-dir -e backend[dev]
```

运行 API：

```powershell
cd backend
..\.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
```

数据库迁移：

```powershell
cd backend
..\.venv\Scripts\alembic.exe upgrade head
```

TXT 解析 worker 第一版：

```powershell
cd D:\listen_book
.venv\Scripts\python.exe -m app.workers.parse_books
```

## Frontend

依赖安装：

```powershell
cd frontend
npm install --no-audit --no-fund
```

开发服务器：

```powershell
cd frontend
npm run dev
```

生产构建：

```powershell
cd frontend
npm run build
```

## PostgreSQL Setup

当前默认连接串在 `.env.example`：

```text
postgresql+psycopg://listen_book_app:change-me@localhost:5432/listen_book
```

需要在 PostgreSQL 里创建对应数据库和用户，或者把 `.env` 改成已有账号。

示例 SQL：

```sql
CREATE USER listen_book_app WITH PASSWORD 'change-me';
CREATE DATABASE listen_book OWNER listen_book_app;
GRANT ALL PRIVILEGES ON DATABASE listen_book TO listen_book_app;
```
