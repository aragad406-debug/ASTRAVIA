# Implementation plan and status

## Workspace inspection (start of work)

- The workspace was empty: no source code, no Git repository, no environment files.
- Python 3.13 and PostgreSQL 16 were available. The build environment could not reach PyPI, so dependencies were installed from their official GitHub source repositories; `requirements.txt` lists the normal PyPI packages for every other environment.
- Decision: build from scratch in `astravia/` following the specified structure.

## Key decisions

| Decision | Reason |
|---|---|
| Django templates + progressive JavaScript, no SPA | Essential content renders without JS; one developer can maintain it. |
| Canvas 2D for the starfield and orrery; **no Three.js** | The effects need no 3D engine. Avoids a ~700 KB dependency on every visit. Graceful CSS fallback; reduced motion respected. |
| Bilingual paired fields (`name_en` / `name_ar`) + `LocalizedMixin` | Two languages are fixed by the brief. Paired fields are explicit, queryable, easy to edit side by side, and let the Localization Studio compute gaps exactly. |
| Interface strings in `apps/core/ui.py` with database overrides (`UIString`) | Works without GNU gettext tooling; editors change labels in the studio. |
| Custom email-based `User` model set before the first migration | Required by the brief; avoids a painful later migration. |
| Roles = Django Groups synced from `apps/creator_studio/roles.py` after every `migrate` | Uses Django's permission framework; roles can't drift from code. |
| Registry-driven studio CRUD + dedicated tools | One well-tested set of generic views (permissions, revisions, workflow, audit) instead of 15 hand-written copies; special tools where content needs them (flow editor, dialogue preview, storyboard, localization, media). |
| Structured JSON conditions with a validated interpreter | No `eval`; administrators can express quest/lore/flag/choice logic safely. |
| Editing live content requires publish permission | Non-publishers can't change the public site; drafts and review flow cover their work. |
| Hidden content only via `core.view_hidden_content` | No "secret URL" security. |

## Phases — status

| Phase | Status |
|---|---|
| 1. Workspace & architecture | Done |
| 2. Database & canonical content | Done — 12 apps, migrations, `seed_astravia` (idempotent) |
| 3. Public website | Done — homepage, worlds, characters, story, lore, quests, news, search, pages, SEO, RTL |
| 4. Authentication | Done — registration, login with rate limiting, verification, reset, profile, deletion requests |
| 5. Creator Studio | Done — see `CREATOR_STUDIO_GUIDE.md` |
| 6. API & Unreal integration | Done — `/api/v1/`, OpenAPI schema, token auth, player quest-start endpoint |
| 7. Production readiness | Done — Render blueprint, production settings, deploy check, 81 passing tests on PostgreSQL and SQLite |

## Remaining scope (not implemented)

- Unreal Engine project, gameplay, multiplayer, online services.
- A concrete text-to-speech provider adapter (interface only).
- AI-generated guide dialogue (configuration hook only).
- Drag-and-drop story editing (the flow editor draws the graph; branches are edited in a structured table).
- OAuth / Google Sign-In.
- Arabic labels for model enum choices (e.g. "Chapter", "Side quest") — they currently display in English on Arabic pages.
- Full-text ranking (search is normalized substring matching, adequate at current scale).
