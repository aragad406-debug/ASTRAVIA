# ASTRAVIA Creator Studio guide

URL: `/creator-studio/` · Sign in with a studio account. The first account is created with `python manage.py create_owner`.

## Roles

| Role | Can do |
|---|---|
| Owner | Everything (superuser). Only assignable from the command line. |
| Administrator | All content, publishing, hidden content, team, audit log, site settings |
| Narrative Editor | Story arcs/chapters/nodes/branches, lore, artifacts, cinematics, dialogue |
| World Designer | Worlds and regions |
| Character Editor | Characters, relationships, guide assistants |
| Quest Designer | Quests, objectives, dependencies, rewards, boss encounters, artifacts |
| Localization Editor | Edit text of existing records, glossary, translation reviews, import/export |
| Voice Editor | Voice profiles, generation requests, voice fields on dialogue, audio uploads |
| Media Editor | Media library |
| Reviewer | Approve and publish (on content types they can edit) |
| Read-Only Viewer | View everything in the studio |

Every role can view all studio content. Permissions are checked on the server for every request.

## Publication workflow

Draft → (Submit for review) → In review → (Approve) → Approved → Publish / Schedule → Published → Unpublish / Archive.

- New records start as **drafts** and never appear on the site or API.
- **Preview** opens the public page with `?preview=1` (studio members only) and shows a preview banner.
- **Schedule** sets a future UTC time. The site treats the item as live from that moment; the `publish_scheduled` cron job also updates its stored status.
- **Editing live content requires publishing permission**, because changes appear immediately.
- Chapters whose story graph has errors cannot be published or approved.
- Every transition is recorded in Publication history and the audit log.

## Revisions

Each save creates a revision. *Revisions* lists them; open one to compare with the current version or the previous revision, and *Restore* to copy its content back. Restoring never changes publication status and is itself saved as a new revision.

## Content sections

- **Worlds** — names, taglines, descriptions, capital, ruler, theme and colours (used by the procedural planet), hero image, background video, Unreal level path, 3D reference, unlock conditions, visibility (public / teaser / hidden). Regions are edited inline.
- **Characters** — category, world, biography, appearance, personality, motivation, fears, *secrets* (studio-only, never public), ages, colour, portrait, gallery, 3D/skeletal/animation references. Relationships are edited inline from the character's side.
- **Story arcs / chapters** — chapter order, type, body, closing line, spoiler flag, ending type, prerequisites, required discoveries, unlock conditions. Nodes are edited inline on the chapter. **Flow editor** (button on the chapter) draws the graph, validates it (one start, reachable nodes, no dead ends, endings terminate, choice labels and translations, condition references) and edits branches.
- **Cinematics** — metadata and storyboard scenes; *Storyboard* view. A cinematic is only "rendered" when a rendered video is attached.
- **Quests** — objectives, prerequisites (circular chains are rejected), rewards, start/completion/failure conditions, required items, unlocked lore.
- **Boss encounters** — boss, arena, required quest state, health bar, phases with thresholds and dialogue triggers. This is data for Unreal; combat is not simulated here.
- **Dialogue** — speaker, guide, category, text EN/AR, trigger event, page context (guide lines), conditions, emotion, delivery notes, duration, priority, voice EN/AR, choices. *Preview dialogue* simulates player state and shows which line/choices pass.
- **Guide assistants** — the Celestial Guide (مرشدة الكواكب) and any others: purpose, intro, voice profile, languages, related worlds, trigger pages, position, primary flag. Their lines are Dialogue entries with *Guide* set. The website widget picks lines by page and world, then priority.
- **Voice profiles** — provider, voice id, language, rate, pitch, pronunciation notes. *Request generation* on a dialogue records a request; without a configured provider it is marked "No provider configured" and nothing is generated. Upload recorded audio instead.
- **Lore & artifacts**, **Announcements**, **Pages** — as named.
- **Media library** — upload images (PNG, JPEG, WebP, GIF, AVIF), audio (MP3, OGG, WAV, FLAC, M4A), video (MP4, WebM), PDF. Files are checked by content signature and size; images are decoded and need alt text. SVG/HTML are refused. *External reference* records large assets kept elsewhere (Unreal paths, bucket URLs).

## Conditions (structured JSON)

Empty `{}` means "always". Shapes:

```json
{"all": [ ... ]}                      every part must hold
{"any": [ ... ]}                      at least one
{"not": { ... }}                      negation
{"quest": "shatter-the-crown", "state": "completed"}   states: available, active, completed, failed
{"lore": "eilens-last-letter"}        lore discovered
{"item": "rayyans-toy"}               item held
{"world_visited": "everfrost"}
{"choice": "zerath_battle", "equals": "crystal"}
{"flag": "crown_broken", "equals": true}
{"page": "home"}                      website context (guide lines)
```

Referenced quests, lore, items and worlds must exist. Maximum 8 levels and 64 parts. Nothing is executed; the server interprets this grammar only.

**Consequences** (branches and choices) are a list of: `{"flag": "x", "value": true}`, `{"choice": "key", "value": "option"}`, `{"quest": "slug", "state": "active"}`, `{"lore": "slug"}`, `{"item": "slug"}`.

## Localization studio

- *Translation status*: per content type, records and fields written in only one language.
- *Missing translations*: filterable list with edit/compare links.
- *Compare*: EN and AR side by side; mark fields reviewed. Reviews go stale automatically when text changes.
- *Export* (all or missing only) → JSON; *Import* updates only localized fields, respects permissions and publication rules, and creates revisions.
- *Interface text*: override any button or label without code.
- Story text uses formal Modern Standard Arabic. Keep names consistent with the *Terminology glossary*.

## Administration

- **Team & roles** — add a member by email and choose roles. New members set a password with "Forgot your password?" (requires email delivery).
- **Deletion requests** — complete (deletes the account and its progress) or cancel.
- **Audit log** — sign-ins (including failures), content, publication, roles, settings, translations. No passwords or tokens are ever recorded.
- **Site settings** — homepage copy, trailer, ambient audio (never autoplays), contact, social links, newsletter toggle.

## Adding a text-to-speech provider

In `apps/dialogues/voice.py`, subclass `VoiceProvider`, implement `synthesize()` to return `(audio_bytes, mime_type)` or raise `VoiceProviderError`, and register it: `PROVIDERS["myprovider"] = MyProvider`. Set `VOICE_PROVIDER=myprovider` and `VOICE_PROVIDER_API_KEY` on the server, and set the voice profile's provider to *External*. Successful results are saved to the media library flagged as generated.
