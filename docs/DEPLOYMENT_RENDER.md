# Deploying to Render

Nothing in this repository creates paid infrastructure automatically. Review plans and costs in Render before applying the blueprint.

## Option A — Blueprint (recommended)

1. Push the repository to GitHub (never commit `.env`).
2. Render dashboard → **New → Blueprint** → choose the repository. Render reads `render.yaml`:
   - `astravia-db` PostgreSQL database
   - `astravia` web service (`./build.sh`, pre-deploy `migrate` + `createcachetable`, gunicorn, health check `/healthz/`, 5 GB persistent disk at `/var/data` for media)
   - `astravia-publish-scheduled` cron job every 10 minutes
3. Fill in the secrets marked `sync: false` (email settings, owner email/password).
4. Deploy. After the first successful deploy, open **Shell** on the web service:

```bash
python manage.py seed_astravia
python manage.py create_owner --from-env
```

Then remove `ASTRAVIA_OWNER_PASSWORD` from the environment.

## Option B — Manual

- **Database:** New PostgreSQL. Copy its internal connection string.
- **Web service:** Python runtime.
  - Build command: `./build.sh`
  - Pre-deploy command: `python manage.py migrate --noinput && python manage.py createcachetable`
  - Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
  - Health check path: `/healthz/`

## Environment variables

| Variable | Required | Notes |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | yes | `config.settings.production` |
| `SECRET_KEY` | yes | 40+ random characters (blueprint generates one) |
| `DATABASE_URL` | yes | Render PostgreSQL connection string |
| `ALLOWED_HOSTS` | custom domains | Render hostname is added automatically from `RENDER_EXTERNAL_HOSTNAME` |
| `CSRF_TRUSTED_ORIGINS` | custom domains | `https://your-domain` |
| `SITE_URL` | recommended | canonical URLs and sitemap, e.g. `https://your-domain` |
| `MEDIA_STORAGE` | yes | `local` (with disk) or `s3` |
| `MEDIA_ROOT` | with `local` | `/var/data/media` |
| `SERVE_MEDIA` | with `local` | `True` to serve uploads through Django |
| `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_CUSTOM_DOMAIN` | with `s3` | any S3-compatible provider |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | for email | without them, emails are discarded in production |
| `ASTRAVIA_OWNER_EMAIL`, `ASTRAVIA_OWNER_PASSWORD` | first setup | used once by `create_owner --from-env` |
| `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`, `SECURE_SSL_REDIRECT` | optional | defaults: 1 year, off, off, on |
| `VOICE_PROVIDER`, `VOICE_PROVIDER_API_KEY` | optional | see Creator Studio guide |
| `LOG_LEVEL`, `WEB_CONCURRENCY` | optional | |

## Media

Render's normal filesystem is replaced on every deploy. Either keep the persistent disk (single instance only) or switch to `MEDIA_STORAGE=s3` (recommended; scales to several instances). The production CSP allows `https:` images/media when `s3` is selected.

## Checks after deploy

```bash
curl https://<host>/healthz/          # {"status": "ok", "database": "ok"}
python manage.py check --deploy       # in the Render shell
```

## Custom domain

Add it under the service's **Settings → Custom Domains**, then update `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` and `SITE_URL`, and redeploy.

## Migrations

They run in the pre-deploy step; a failed migration stops the release before traffic switches. Never reset the production database to resolve a migration problem — write a corrective migration and back up first (`pg_dump`, see README).
