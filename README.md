# dvla-ai-assistant

A professional Python + Streamlit application for an AI-powered DVLA Ghana support assistant (DVLA Assist).

## Project overview

The app:

- Collects user questions in a Streamlit interface
- Grounds answers with DVLA Ghana domain knowledge
- Calls **Google Gemini** for responses (`google-generativeai`)

## Setup (local)

1. Create and activate a virtual environment:

   - `python3 -m venv .venv`
   - `source .venv/bin/activate`

2. Install dependencies:

   - `pip install -r requirements.txt`

3. Configure environment variables:

   - `cp .env.example .env`
   - Set `GEMINI_API_KEY` and any optional variables (see `.env.example`).

## Run locally

```bash
streamlit run app.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

## Streamlit Community Cloud (free hosting)

You can host this app on **[Streamlit Community Cloud](https://streamlit.io/cloud)** so others get a public HTTPS link without running your own server.

### 1. Put the app on GitHub

Push this project to a GitHub repository. If the app lives in a subfolder, note the path (for example `dvla-ai-assistant/`).

### 2. Connect Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
2. **New app** → pick the repo and branch (usually `main`).
3. **Main file path:** set to `app.py` if the repo root *is* this project, or e.g. `dvla-ai-assistant/app.py` if the repo root is one level above.
4. **Python version:** use **3.11** (Advanced settings) to match the Dockerfile.
5. Deploy. Streamlit will install from `requirements.txt`.

### 3. Add secrets (required for Gemini)

In the Cloud app: **Settings (gear) → Secrets**, add a TOML block. Minimum:

```toml
GEMINI_API_KEY = "your-key-from-google-ai-studio"
```

Optional:

```toml
MODEL_NAME = "gemini-2.5-flash"
DEBUG = "false"
LOG_LEVEL = "INFO"
```

Alternatively, group under a table (also supported by this app):

```toml
[dvla]
GEMINI_API_KEY = "your-key-here"
MODEL_NAME = "gemini-2.5-flash"
```

[`config/settings.py`](config/settings.py) copies these values into `os.environ` before `Settings()` runs, so **do not commit** `.env` to GitHub; Cloud uses Secrets only.

### 4. Get a Gemini API key

Create a key at [Google AI Studio](https://aistudio.google.com/app/apikey) and paste it into **Secrets** as `GEMINI_API_KEY`.

### 5. Redeploy after secret changes

After editing Secrets, use **Manage app → Reboot** (or trigger a redeploy) so the new values load.

**Note:** Community Cloud does **not** use your `Dockerfile`; it builds from `requirements.txt`. Docker remains useful for VMs, Cloud Run, etc.

## Docker (production-style)

From this directory (where `Dockerfile` and `docker-compose.yml` live):

```bash
cp .env.example .env   # if needed
# Edit .env — at minimum GEMINI_API_KEY

docker compose build
docker compose up -d
```

- Streamlit listens on **8501** inside the container.
- Compose maps **8501:8501** and mounts **`./logs`** to **`/app/logs`** for Loguru output.

### GHCR image on the server

After CI pushes to GitHub Container Registry, set in the server’s `.env` next to `docker-compose.yml`:

```env
DVLA_IMAGE=ghcr.io/your-org/dvla-ai-assistant:latest
```

Then `docker compose pull && docker compose up -d` will use the published image (the compose file uses `image: ${DVLA_IMAGE:-...}`).

## HTTPS (nginx)

A sample reverse-proxy configuration (TLS, security headers, HTTP→HTTPS) is in:

[`deploy/nginx.sample.conf`](deploy/nginx.sample.conf)

Copy it to your server, adjust `server_name` and certificate paths (for example with [Let’s Encrypt](https://letsencrypt.org/) / certbot), reload nginx, and proxy to `127.0.0.1:8501`.

## GitHub Actions deploy

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

- **Trigger:** push to `main`
- **Build:** Docker image from this repo, push to **GHCR** (`ghcr.io/<owner>/<repo>:latest`, lowercased)
- **Deploy:** SSH to your server, `docker login ghcr.io`, `docker compose pull` / `up -d`

### Repository secrets

| Secret | Purpose |
|--------|---------|
| `GHCR_TOKEN` | Login to GHCR (PAT with `write:packages`, or `GITHUB_TOKEN` if your org allows package push from Actions) |
| `SSH_KEY` | Private SSH key for the deploy user |
| `SERVER_IP` | Server hostname or IP |
| `SSH_USER` | SSH username (e.g. `ubuntu`) |
| `DEPLOY_PATH` | *(Optional)* Remote path containing `docker-compose.yml` and `.env` (defaults to `/opt/dvla-ai-assistant` in the script) |
| `GEMINI_API_KEY` | *(Optional)* Listed for your checklist; **recommended** is to keep the key only in the **server** `.env`. Add a custom job if you need the secret in CI. |

On the server, create the deploy directory, clone or copy this project, add `.env` with `GEMINI_API_KEY` (and `DVLA_IMAGE` when using GHCR), then ensure the workflow’s `cd` path matches.

## Production checklist

- [ ] Set **`DEBUG=false`** in production `.env`.
- [ ] **Rotate `GEMINI_API_KEY` periodically** (Google AI Studio / Cloud Console). Revoke old keys after rotation.
- [ ] **Obtain a Gemini API key:** open [Google AI Studio API keys](https://aistudio.google.com/app/apikey), sign in with a Google account, and create a key (free tier subject to Google’s current limits).
- [ ] **HTTPS:** terminate TLS at nginx (or another reverse proxy) using a sample like [`deploy/nginx.sample.conf`](deploy/nginx.sample.conf); redirect HTTP to HTTPS.
- [ ] **Logs:** application logs use **Loguru** with rotation (`10 MB`) and retention (`7 days`) in `logs/` — ensure the `logs` volume or host directory is monitored and disk space is adequate.
- [ ] **Operator access:** if you add admin or maintenance routes later, set **`ADMIN_PASSWORD`** (or equivalent) to a **strong random** value and never commit it.
- [ ] Restrict who can push to `main` and who can view **GitHub Actions secrets**.
- [ ] Prefer **non-root** container runtime where your platform supports it; keep the image updated (`docker compose pull` on deploy).

## Module map (short)

| Area | Path | Role |
|------|------|------|
| Entry | `app.py` | Streamlit UI and chat loop |
| Config | `config/settings.py` | Environment-backed settings |
| AI | `core/ai_engine.py` | Gemini client, streaming, safety hooks |
| Prompts | `core/prompt_builder.py` | System prompt + chat history formatting |
| Knowledge | `knowledge/dvla_knowledge.py` | DVLA Ghana text and disclaimers |
| UI | `ui/` | Components and CSS injection |
| Utils | `utils/logger.py` | Structured logging |

For extending knowledge without changing the Gemini client, see [CONTRIBUTING.md](CONTRIBUTING.md).
