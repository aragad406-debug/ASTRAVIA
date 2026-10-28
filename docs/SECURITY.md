# Security

## Implemented controls

| Area | Implementation |
|---|---|
| Passwords | Django PBKDF2 hashing; minimum 10 characters, similarity/common/numeric validators |
| Sign-in throttling | 5 failures per (IP, email) and 20 per IP in 15 minutes (`apps/core/ratelimit.py`), shared cache (database cache in production) |
| Generic auth responses | Same login error for unknown email and wrong password; password reset always shows the same message; reset requests throttled per IP |
| Email verification | Signed, expiring (3 days) links; no tokens stored; production never logs emails |
| Sessions / CSRF | HttpOnly, SameSite=Lax cookies; Secure cookies and HTTPS redirect in production; CSRF on every form; logout is POST-only |
| Authorization | Every studio view checks `core.access_studio` plus the model permission for the action; publishing, reviewing, hidden content, team, audit and settings have dedicated permissions; editing live content requires publish permission |
| Mass assignment | Studio forms exclude `status`, `published_at`, `revision`, `is_seeded`; status changes only through the workflow service |
| Owner creation | Command line only (`create_owner`); the Owner role can't be granted from the web UI by non-superusers |
| Unpublished / hidden content | Querysets `.published()` / `.visible_to(user)` everywhere; hidden content requires `core.view_hidden_content`; not in sitemap, search or API for anonymous users; returns 404 (indistinguishable from missing) |
| API | Explicit serializer allow-lists; character secrets, delivery notes and conditions never exposed publicly; read-only; throttled |
| Administrator logic | Structured JSON conditions interpreted by a whitelist grammar — no `eval`, no expressions |
| Uploads | Signature sniffing per kind, Pillow decode for images, size limits, SVG/HTML refused, random file names, never executed |
| Output escaping | Django autoescape; user text rendered with `linebreaks` (escaped) |
| Headers | CSP (`script-src 'self'`, no inline scripts), X-Frame-Options DENY, nosniff, Referrer-Policy, COOP, Permissions-Policy, HSTS in production, `X-Robots-Tag: noindex` on private areas |
| Colours in inline styles | Hex-validated at the model, so theme colours can't inject CSS |
| Audit | Logins, failed logins, content, publication, roles, settings, translations, deletions; summaries mentioning secrets are refused |
| Secrets | Environment variables only; `.env` ignored by Git; `.env.example` has placeholders |
| Errors | `DEBUG=False` in production; standalone 500 page with no database access |
| Open redirects | Newsletter `next` validated with `url_has_allowed_host_and_scheme` |

## Operational guidance

- Rotate `SECRET_KEY` only with a plan (it invalidates sessions and verification links).
- Remove `ASTRAVIA_OWNER_PASSWORD` from the environment after the owner exists.
- Enable `SECURE_HSTS_INCLUDE_SUBDOMAINS` (and preload) only when every subdomain is HTTPS-only.
- Give service accounts the narrowest role that works; keep their API tokens in CI secrets.
- Review the audit log for repeated `login_failed` events.
- Dependency auditing: run `pip install pip-audit && pip-audit -r requirements.txt` regularly (not run in the build environment, which had no PyPI access).

## Not yet covered

- Two-factor authentication for studio accounts.
- Malware scanning of uploaded files.
- Server-side validation for quest objective progress and rewards (needed before any online play).
