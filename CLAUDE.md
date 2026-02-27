# CLAUDE.md — dcoops-bot

## Project Overview

**dcoops-bot** is a Discord bot written in Python that supports music playback, sound binds, image sharing, jigsaw puzzle creation, text-to-speech, and user voice-join/leave messages. It optionally pairs with a Flask web application (soundboard UI) that communicates with the bot via RabbitMQ.

---

## Repository Layout

```
dcoops-bot/
├── dcoops/                  # Discord bot package
│   ├── main.py              # Bot entry point — registers all cogs and starts
│   ├── bot/                 # Cog modules (one file per feature)
│   │   ├── music.py         # Audio playback (yt-dlp, FFmpeg, binds)
│   │   ├── files.py         # File/bind upload, load, delete commands
│   │   ├── utilities.py     # List files/binds commands
│   │   ├── activity.py      # Bot presence (Resident Evil status)
│   │   ├── groans.py        # Combined audio+video clip creation
│   │   ├── jigsaw.py        # Jigsaw puzzle creation via jigsawexplorer.com
│   │   ├── events.py        # Voice state event listeners + helper fns
│   │   ├── custom_messages.py  # Per-user TTS join/leave messages
│   │   ├── imgur.py         # Imgur upload helpers (image and video)
│   │   └── tts.py           # Google TTS (gTTS) wrapper
│   ├── requirements.txt     # Bot Python dependencies
│   ├── env.test             # Environment variable template
│   └── Dockerfile           # Bot container (Ubuntu 20.04 + ffmpeg)
│
├── dcoopsdb/                # Shared database layer (SQLAlchemy + MySQL)
│   ├── db.py                # Engine + scoped Session factory
│   └── models.py            # ORM models: File, Bind, CustomMessage, Settings
│
├── webapp/
│   ├── backend/             # Flask web app
│   │   ├── app.py           # Flask app + Discord OAuth2 + RabbitMQ publisher
│   │   ├── soundboard.py    # Soundboard helper (loads bind names from DB)
│   │   ├── config.py        # RabbitMQ connection params
│   │   ├── gunicorn.conf.py # Gunicorn config (1 worker)
│   │   ├── templates/       # Jinja2 templates
│   │   │   ├── soundboard.html
│   │   │   └── basic_form.html
│   │   ├── requirements.txt # Flask/web dependencies
│   │   └── Dockerfile       # Backend container
│   └── frontend/            # React/TypeScript app (CRA scaffold)
│       ├── src/App.tsx       # Default CRA placeholder (not yet developed)
│       └── package.json
│
├── alembic/                 # Database migrations
│   ├── env.py               # Alembic env (reads DB creds from .env)
│   └── versions/            # Migration scripts
│
├── docker-compose.yml       # Full stack: bot + MySQL + webapp + frontend + RabbitMQ
├── docker-compose-noweb.yml # Minimal stack: bot + MySQL only
├── Makefile                 # Convenience targets (start, start-webapp, lint)
├── run_ci.py                # CI script: runs black --check + flake8
├── alembic.ini              # Alembic configuration
└── setup.py                 # Package setup
```

---

## Architecture

### Discord Bot (`dcoops/`)

- Uses **discord.py 1.7.3** with the `commands.Bot` framework.
- Command prefix: `!` (also responds to direct mentions).
- All features are implemented as **Cogs** and registered in `main.py`.
- Audio playback requires **FFmpeg** at runtime.
- YouTube downloading uses **yt-dlp**; downloaded files are cached in `dcoops/video-cache/`.

### Database (`dcoopsdb/`)

- **MySQL** via **SQLAlchemy 1.4** and **PyMySQL**.
- `db.py` builds the SQLAlchemy URL from environment variables and creates a `scoped_session` factory called `Session`.
- Models use a shared `BaseFile` mixin that provides `load`, `load_all`, `delete`, `exists`, and `random` class methods.
- **Alembic** is used for schema migrations. The `alembic/env.py` reads DB credentials from `.env` in the working directory.

### Web Application (`webapp/`)

- **Backend**: Flask + Gunicorn, Discord OAuth2 via `Flask-Discord`. Communicates with the bot by publishing messages to a RabbitMQ queue (`hello`).
- **Frontend**: React/TypeScript (Create React App). Currently contains only the default CRA scaffold — not yet implemented.
- **RabbitMQ**: Message broker that bridges the web app and the bot. The bot subscribes to the `hello` queue to receive play commands. Only active when `WEB_APP_ACTIVE=true`.

> **Note**: `webapp/backend/app.py` imports `from webapp.backend.src.api import dcoops_api`, but the `webapp/backend/src/` directory does not exist. This import will fail at runtime. The `dcoops_api` blueprint is referenced but missing.

---

## Environment Variables

### Bot (`.env` in project root or `dcoops/.env`)

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from Discord Developer Portal |
| `DB_USERNAME` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_HOST` | MySQL host (e.g., `localhost` or Docker service name `mysql`) |
| `DB_PORT` | MySQL port (default `3306`) |
| `WEB_APP_ACTIVE` | Set to any truthy value to enable RabbitMQ + webapp integration |
| `TEST_SERVER` | Discord Guild (server) ID used by RabbitMQ-triggered commands |
| `IMGUR_CLIENT_ID` | Imgur API client ID |
| `IMGUR_CLIENT_SECRET` | Imgur API client secret |

### Web Backend (`.env` in `webapp/backend/`)

| Variable | Description |
|---|---|
| `FLASK_SECRET_KEY` | Flask session secret key |
| `DISCORD_CLIENT_ID` | Discord OAuth2 app client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth2 app client secret |
| `DISCORD_REDIRECT_URI` | OAuth2 callback URI |
| `DISCORD_BOT_TOKEN` | Bot token (used by Flask-Discord) |

Use `dcoops/env.test` as a reference template for bot environment variables.

---

## Bot Commands Reference

All commands use the `!` prefix (case-insensitive).

| Command | Cog | Description |
|---|---|---|
| `!play <query>` | Music | Play a local bind by alias, or a URL |
| `!yt <url>` | Music | Stream from YouTube or any yt-dlp source |
| `!stream <url>` | Music | Same as `!yt` |
| `!volume <0-100>` | Music | Adjust playback volume |
| `!stop` | Music | Disconnect from voice channel |
| `!join <channel>` | Music | Join a specific voice channel |
| `!yt_bind <url> <start> <stop> <alias>` | Music | Create a bind from a YouTube clip |
| `!groans [alias]` | Music | Play a bind and show its image simultaneously |
| `!upload <alias>` | Files | Upload an attached file as a file/bind |
| `!upload_embed <url> <alias>` | Files | Upload a URL as a file/bind |
| `!load <alias>` | Files | Send a stored file URL to the channel |
| `!delete_file <alias>` | Files | Delete a stored file |
| `!delete_bind <alias>` | Files | Delete a stored bind |
| `!list_files` | Utilities | List all stored files for this server |
| `!list_binds` | Utilities | List all stored binds for this server |
| `!yt_groans <url> <start> <stop> <alias>` | Groans | Create a "groan" (audio bind + Imgur video) from YouTube |
| `!delete_groans <alias>` | Groans | Delete a groan (removes both file and bind) |
| `!jigsaw [pieces]` | Jigsaw | Create a jigsaw puzzle from an attached image |
| `!set_join_message <message>` | Messages | Set a custom TTS join message (use `%name` as placeholder) |
| `!set_leave_message <message>` | Messages | Set a custom TTS leave message |

---

## Database Models

### `File` (table: `files`)
Stores image/video URLs associated with an alias and server.
- `alias` (str, 256) — Unique per server
- `file_url` (str, 256)
- `server` (str, 32) — Discord Guild ID

### `Bind` (table: `binds`)
Stores audio file URLs associated with an alias and server (same structure as `File`).
- `alias`, `file_url`, `server` — same as `File`

### `CustomMessage` (table: `custom_messages`)
Per-user custom TTS announcement messages.
- `server`, `user_id`, `message_type` (`join_message` or `leave_message`), `message`

### `Settings` (table: `settings`)
Per-server settings (currently just a placeholder with `server` column).

---

## Development Workflows

### Running the Bot (no web app)

```bash
# Using Docker Compose (recommended)
make start
# or directly:
docker-compose -f docker-compose-noweb.yml up

# Or run locally (requires MySQL and env vars set):
python3 -m dcoops.main
```

### Running the Full Stack (with web app)

```bash
make start-webapp
# or:
docker-compose -f docker-compose.yml up --build webapp
```

### Database Migrations

Run Alembic from the project root (requires a `.env` with DB credentials):

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade one step
alembic downgrade -1
```

### Linting

The project uses **Black** for formatting and **flake8** for linting.

```bash
# Format code (modifies files)
make lint
# Equivalent to:
black --exclude 'venv/*|alembic/*' .
flake8 --ignore=E501,E402 --exclude=venv/,alembic/

# Check only (no modifications — used in CI)
python3 run_ci.py
```

Ignored rules:
- `E501` — Line too long (no line length limit enforced)
- `E402` — Module level import not at top of file

Excluded directories: `venv/`, `alembic/`

---

## Continuous Integration

GitHub Actions runs on every push (`.github/workflows/continous_integration.yml`):

1. Sets up Python 3.9
2. Installs `flake8` and `black`
3. Runs `python3 run_ci.py` — checks formatting and linting

A separate CodeQL workflow runs on pushes/PRs to `main` for Python security analysis.

**Before pushing**, always ensure CI passes locally:
```bash
python3 run_ci.py
```

---

## Key Conventions

1. **Cog pattern**: Each feature group is a `commands.Cog` subclass in its own file under `dcoops/bot/`. Register new cogs with `bot.add_cog(...)` in `dcoops/main.py`.

2. **Database access**: Always use `dcoopsdb.db.Session` as a context manager (`with Session() as session:`). Call `session.commit()` and `session.close()` explicitly within the block.

3. **Server scoping**: All DB queries filter by `server` (Discord Guild ID as a string). Never query across servers.

4. **Audio playback**: Audio commands require voice channel membership. The `ensure_voice` before-invoke hook in `Music` auto-joins the author's voice channel.

5. **File classification**: In `files.py`, audio extensions (`.mp3`, `.wav`, `.ogg`, `.webm`, `.m4a`) create `Bind` records; everything else creates `File` records.

6. **Alias normalization**: All aliases are lowercased before storing or querying.

7. **Import path**: `dcoops/main.py` adds the project root to `sys.path`, enabling absolute imports like `from dcoopsdb.models import Bind`.

8. **Formatting**: Run `black` before committing. The project intentionally allows long lines (E501 ignored).

9. **No tests**: There are no unit or integration tests beyond linting. The CI only checks code style.

---

## Known Issues / Technical Debt

- `webapp/backend/app.py` imports `from webapp.backend.src.api import dcoops_api` but `webapp/backend/src/` does not exist. This will cause an `ImportError` at startup. The `dcoops_api` blueprint is referenced but never defined in the repo.
- The React frontend (`webapp/frontend/`) is the default Create React App scaffold with no actual functionality implemented.
- `dcoops/main.py` has two `import sys` and two `import asyncio` statements.
- `webapp/backend/app.py` registers the `dcoops` blueprint twice (once mid-file, once at the bottom).
- `list_groans` in `utilities.py` has a broken SQLAlchemy join (uses `File.alias == Bind.alias` as a filter condition, not a join predicate).
- The `Jigsaw` cog constructor is missing `self` in `def __init__` — it works as a Cog only because discord.py handles instantiation.
