# ASTRAVIA · أسترافيا

Official website, content platform and game-content API for **ASTRAVIA**, a cosmic-fantasy action RPG in pre-production.

This repository contains:

- **Public website** (English / Arabic, RTL-aware): homepage with an animated orrery, worlds, characters, story arcs and chapters, memory archive (lore), quests, news, search, legal pages, sitemap.
- **ASTRAVIA Creator Studio** (`/creator-studio/`): a custom, role-protected CMS for worlds, characters, relationships, story arcs/chapters/branching nodes, dialogue, guide assistants, voices, quests, boss encounters, cinematics, lore, artifacts, media, announcements, pages, localization, team roles, revisions, publishing and audit.
- **Versioned content API** (`/api/v1/`) designed for a future Unreal Engine 5 client.
- **Canonical seed** of the six worlds, sovereigns, story, quests, dialogue and lore.

> There is no Unreal Engine project, playable build, or online game service in this repository. The API and data model are prepared for one. See `docs/UNREAL_ENGINE_INTEGRATION.md`.

---

## 1. Required software

| Software | Version |
|---|---|
| Python | 3.12 or 3.13 (developed and tested on 3.13) |
| PostgreSQL | 14+ (tested on 16) — SQLite works for quick local runs |
| Git | any recent |

## 2. Setup

```bash
git clone <your repo> astravia && cd astravia
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```

Edit `.env`. At minimum for development:

```ini
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
DATABASE_URL=postgres://astravia:yourpassword@127.0.0.1:5432/astravia
```

Leave `DATABASE_URL` empty to fall back to `db.sqlite3` (development only).

### Local PostgreSQL

```sql
CREATE USER astravia WITH PASSWORD 'yourpassword' CREATEDB;
CREATE DATABASE astravia OWNER astravia;
```

`CREATEDB` lets the test runner create its temporary test database.

## 3. Database, content and owner account

```bash
python manage.py migrate            # creates tables and the 11 studio roles
python manage.py seed_astravia      # canonical worlds, characters, story, quests, dialogue, lore (safe to rerun)
python manage.py create_owner       # prompts for email + password
# or, non-interactively:
#   set ASTRAVIA_OWNER_EMAIL / ASTRAVIA_OWNER_PASSWORD, then
python manage.py create_owner --from-env
```

There is no web route that creates an owner. `seed_astravia` never overwrites edited content; `--refresh` updates only seeded records that were never revised in the studio.

## 4. Run

```bash
python manage.py runserver
```

- Website: http://127.0.0.1:8000/ (Arabic: `?lang=ar`)
- Creator Studio: http://127.0.0.1:8000/creator-studio/
- API: http://127.0.0.1:8000/api/v1/ · docs `/api/docs/` · OpenAPI `/api/v1/schema/`
- Health check: `/healthz/`

## 5. Tests

```bash
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test tests
# Windows PowerShell:
$env:DJANGO_SETTINGS_MODULE="config.settings.test"; python manage.py test tests
```

Uses PostgreSQL when `DATABASE_URL` is set, otherwise SQLite. 81 tests cover authentication, rate limiting, worlds, characters, story graphs, conditions, dialogue, quests, studio permissions, publishing, revisions, media validation, localization, the API's hidden/unpublished-content protection, and production settings.

## 6. Static files

```bash
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic
```

Production serves static files with WhiteNoise (compressed, hashed filenames). Fonts are self-hosted (OFL licences in `static/fonts/licenses/`).

## 7. Email

Set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`.

- Development without `EMAIL_HOST`: emails (verification and reset links) print to the terminal.
- Production without `EMAIL_HOST`: emails are discarded (never logged). Verification and password reset won't arrive until a provider is configured.

## 8. Optional integrations

- **Voice (text-to-speech):** no provider ships enabled. Upload recorded audio in the media library and attach it to dialogue. To add a provider, see `apps/dialogues/voice.py` and `docs/CREATOR_STUDIO_GUIDE.md`. Keys go in `VOICE_PROVIDER` / `VOICE_PROVIDER_API_KEY` (server-side only).
- **AI guide dialogue:** the Celestial Guide is fully rule-based. `GUIDE_AI_PROVIDER` / `GUIDE_AI_API_KEY` and the `ai_enabled` flag exist as configuration hooks only; no AI provider is implemented or called.

## 9. Media storage

- `MEDIA_STORAGE=local` stores uploads in `MEDIA_ROOT`. On Render this **must** be a persistent disk (the default filesystem is wiped on each deploy). Set `SERVE_MEDIA=True` to let Django serve them (fine at small scale).
- `MEDIA_STORAGE=s3` uses S3-compatible object storage (AWS S3, Cloudflare R2, Backblaze B2): `pip install -r requirements-s3.txt` and set the `AWS_*` variables. Recommended for production.

Replacement artwork: upload in **Creator Studio → Media library**, then select it as a world's hero image, a character's portrait, etc. Until then the site renders procedural planets and sigils, never broken images.

## 10. Deploy to Render

See `docs/DEPLOYMENT_RENDER.md`. Summary: push to GitHub → Render → New → Blueprint → select the repo (uses `render.yaml`) → fill the `sync: false` secrets → deploy → open a Render Shell and run `python manage.py seed_astravia` and `python manage.py create_owner --from-env`.

## 11. Custom domain

Add the domain in Render, then set `ALLOWED_HOSTS=your-domain`, `CSRF_TRUSTED_ORIGINS=https://your-domain`, `SITE_URL=https://your-domain`. Once the whole domain is HTTPS-only, consider `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`.

## 12. Unreal Engine 5

See `docs/UNREAL_ENGINE_INTEGRATION.md` for the API contract, authentication model and example requests.

## 13. Backups

Render PostgreSQL paid plans include daily backups. Manual backup/restore:

```bash
pg_dump --format=custom --no-owner "$DATABASE_URL" > astravia-$(date +%F).dump
pg_restore --clean --no-owner --dbname "$DATABASE_URL" astravia-YYYY-MM-DD.dump
```

Back up uploaded media separately (the persistent disk or the bucket).

## 14. Troubleshooting

| Problem | Fix |
|---|---|
| `ImproperlyConfigured: SECRET_KEY must be set` | Production needs a 40+ character `SECRET_KEY`. |
| `DATABASE_URL must be set in production` | Attach the Render database or set the variable. |
| `DisallowedHost` | Add the host to `ALLOWED_HOSTS` (Render's own hostname is added automatically). |
| CSRF failure on forms in production | Add `https://your-domain` to `CSRF_TRUSTED_ORIGINS`. |
| Uploaded images disappear after deploy | Use a persistent disk or `MEDIA_STORAGE=s3`. |
| Studio says "doesn't have access" | Assign a role in Creator Studio → Team & roles, or run `create_owner`. |
| `psycopg` import error locally | `pip install "psycopg[binary]"`. |
| Tests can't create the database | Give the PostgreSQL user `CREATEDB`. |

## Documentation

`docs/IMPLEMENTATION_PLAN.md` · `docs/ARCHITECTURE.md` · `docs/DATABASE_DESIGN.md` · `docs/CREATOR_STUDIO_GUIDE.md` · `docs/UNREAL_ENGINE_INTEGRATION.md` · `docs/DEPLOYMENT_RENDER.md` · `docs/SECURITY.md`
