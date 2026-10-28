# Architecture

```
Browser ──► Django (gunicorn on Render)
              ├── Public website (server-rendered templates + small JS modules)
              ├── Creator Studio (/creator-studio/, Django auth + Groups)
              ├── Content API (/api/v1/, Django REST Framework, read-only + player endpoints)
              └── Django admin (/admin/, superuser fallback only)
            PostgreSQL ◄─ ORM
            Media: persistent disk or S3-compatible bucket
Unreal Engine 5 client (future) ──► /api/v1/ (JSON)
```

## Apps

| App | Responsibility |
|---|---|
| `core` | Abstract models (timestamps, publication, visibility, localization, search), `SiteConfiguration`, `Page`, `UIString`, revisions, publication records, audit log, conditions engine, rate limiting, middleware, public home/search/pages, seed and management commands |
| `accounts` | Email-based `User`, `UserProfile`, `AccountDeletionRequest`, sign-in/registration/verification/reset/profile |
| `media_library` | `MediaAsset` and signature-based upload validation |
| `worlds` | `World`, `Region` |
| `characters` | `Character`, `CharacterRelationship` |
| `narrative` | `StoryArc`, `StoryChapter`, `StoryNode`, `StoryBranch`, `LoreEntry`, `Artifact`, `Cinematic`, `CinematicScene`, story-graph validation/layout |
| `quests` | `Quest`, `QuestObjective`, `QuestDependency`, `QuestReward`, `PlayerQuestState`, `BossEncounter`, `BossPhase`, quest state services |
| `dialogues` | `DialogueEntry`, `DialogueChoice`, `GuideAssistant`, `VoiceProfile`, `VoiceGenerationRequest`, guide line selection, TTS provider interface |
| `localization` | `GlossaryTerm`, `TranslationReview` |
| `announcements` | `Announcement` |
| `creator_studio` | Section registry, generic content views, tools, roles, studio context |
| `api` | Serializers, viewsets, URL routing, pagination |

## Cross-cutting rules

- **Publication:** `PublishableModel.status` ∈ draft, in_review, approved, scheduled, published, archived. Public code only uses `.published()`, `.public()` or `.visible_to(user)`. Scheduled items are live once `publish_at` passes; `publish_scheduled` (cron) also flips the stored status.
- **Visibility:** public, teaser (name/teaser only), hidden (404 unless `core.view_hidden_content`).
- **Localization:** `obj.loc("field")` picks the active language with fallback; `missing_translations()` powers the studio.
- **Search:** each searchable model stores a normalized `search_document` (case-folded, Arabic diacritics removed, alef/ya/ta-marbuta unified). The same normalization is applied to queries.
- **Conditions:** `apps/core/conditions.py` — grammar validation, reference checks, evaluation.
- **Revisions:** every studio save snapshots the record (`ContentRevision`); restore never changes publication state.
- **Audit:** `apps/core/audit.record()` with a scrubber that refuses summaries mentioning secrets.

## Frontend

- `static/css/astravia.css` — design tokens, logical properties (RTL without overrides), reduced-motion and forced-colors support.
- `static/js/cosmos.js` — starfield (Canvas 2D), pauses when hidden, static frame with reduced motion.
- `static/js/orrery.js` — homepage orrery driven by database data in a JSON script block; labels are real links.
- `static/js/guide.js` — Celestial Guide widget using `/api/v1/guides/<slug>/lines/`.
- `static/js/studio.js` — studio nav, inline rows, JSON checks, story-flow SVG.
- No inline scripts; CSP is `script-src 'self'`.

Typefaces (self-hosted, OFL): Marcellus (Latin display), Jost (Latin UI/body), Reem Kufi (Arabic display), IBM Plex Sans Arabic (Arabic UI/body), Amiri (formal Arabic long-form story text).
