# Unreal Engine 5 integration

**Status:** this repository contains the content backend and API only. No Unreal project, gameplay code or game server exists yet. Django manages content (worlds, characters, quests, dialogue, lore, cinematics, localization); Unreal Engine 5 will own rendering, combat, AI, physics and real-time play.

## Contract

- Base URL: `https://<your-site>/api/v1/`
- Format: JSON, UTF-8. Localized text is always `{"en": "...", "ar": "..."}`.
- Only published content is returned. Draft, in-review and archived content returns 404.
- Lists are paginated: `{"count", "next", "previous", "results"}`; `?page=` and `?page_size=` (max 100).
- Machine-readable schema: `GET /api/v1/schema/` (OpenAPI 3).
- Version policy: breaking changes go to `/api/v2/`; additive fields may appear in v1.

## Endpoints the game will use

| Purpose | Request |
|---|---|
| World list / detail (regions, Unreal level path, colours) | `GET /worlds/`, `GET /worlds/{slug}/` |
| Characters (biography, relationships, skeletal mesh, animation refs) | `GET /characters/?world={slug}`, `GET /characters/{slug}/` |
| Quests (objectives, prerequisites, rewards) | `GET /quests/?world={slug}`, `GET /quests/{slug}/` |
| Dialogue by trigger | `GET /dialogues/?trigger=boss_start:zerath`, `GET /dialogues/{key}/` |
| Branching story graph | `GET /story-arcs/{arc}/chapters/{chapter}/` |
| Boss encounter data | `GET /encounters/`, `GET /encounters/{slug}/` |
| Cinematic metadata (Unreal Level Sequence paths, scenes) | `GET /cinematics/{slug}/` |
| Lore | `GET /lore/?world={slug}`, `GET /lore/{slug}/` |
| Interface strings + glossary | `GET /localization/` |
| Public configuration | `GET /site-config/` |

## Example: world detail

`GET /api/v1/worlds/everfrost/` (long text truncated here):

```json
{
  "slug": "everfrost",
  "order": 1,
  "visibility": "public",
  "name": {"en": "Everfrost", "ar": "إيفرفروست"},
  "capital": {"en": "Crystalheim", "ar": "كريستالهايم"},
  "ruler": "zerath",
  "theme": "frost",
  "colors": {"primary": "#9FE4FF", "secondary": "#16284F", "accent": "#E6F4FF"},
  "hero_image": null,
  "regions": [
    {"slug": "crystalheim", "name": {"en": "Crystalheim", "ar": "كريستالهايم"}, "kind": "city", "order": 1,
     "description": {"en": "The capital, preserved at the moment the winter came.", "ar": "العاصمة، محفوظةٌ عند اللحظة التي حلّ فيها الشتاء."}}
  ],
  "unreal_level_path": "",
  "model_3d_reference": ""
}
```

Set `unreal_level_path` (e.g. `/Game/Maps/Everfrost/L_Crystalheim`) in the Creator Studio once levels exist.

## Example: dialogue with choices

`GET /api/v1/dialogues/zerath-boss-intro/`

```json
{
  "key": "zerath-boss-intro",
  "speaker": "zerath",
  "category": "boss_intro",
  "text": {"en": "You have walked through my city and touched nothing. Do the same here, and you may leave.",
           "ar": "عبرتَ مدينتي ولم تمسّ شيئًا. افعل الشيء نفسه هنا، ولك أن ترحل."},
  "world": "everfrost",
  "quest": "shatter-the-crown",
  "trigger_event": "boss_start:zerath",
  "emotion": "cold",
  "display_duration_ms": 6000,
  "subtitles_enabled": true,
  "voice": {"en": null, "ar": null},
  "choices": [
    {"order": 1, "text": {"en": "I came for her.", "ar": "جئتُ من أجلها."}, "next": "zerath-why", "consequences": []},
    {"order": 2, "text": {"en": "Who is she?", "ar": "من تكون؟"}, "next": "zerath-why", "consequences": []}
  ],
  "conditions": null
}
```

`conditions` is `null` for anonymous callers because conditions can reference hidden content. Authorized services receive the structured condition JSON (grammar in `docs/CREATOR_STUDIO_GUIDE.md`).

## Sample Unreal-side flow (specification)

A recommended pattern, not code that exists in this repository:

1. **At build/cook time**, an editor utility or CI step (authenticated with a service token, see below) downloads worlds, characters, quests, dialogue, encounters and localization, and writes them into Unreal `DataTable`/`DataAsset` files. The shipped game reads local data and works offline.
2. **At runtime** (optional), the client may fetch updated public content with `FHttpModule`:

```cpp
// Pseudocode sketch for an Unreal subsystem
TSharedRef<IHttpRequest> Req = FHttpModule::Get().CreateRequest();
Req->SetURL(TEXT("https://<site>/api/v1/dialogues/?trigger=boss_start:zerath"));
Req->SetVerb(TEXT("GET"));
Req->SetHeader(TEXT("Accept"), TEXT("application/json"));
Req->OnProcessRequestComplete().BindUObject(this, &UAstraviaContent::OnDialogue);
Req->ProcessRequest();
// OnDialogue: parse with FJsonSerializer, pick text["ar"] or text["en"] from the player's language,
// play voice[lang] if present, show choices, follow choices[i].next.
```

3. Map `speaker` slugs to character assets, `trigger_event` strings to gameplay events, and `cinematics[].unreal_sequence_path` to Level Sequences.

## Authentication

| Caller | Mechanism |
|---|---|
| Anyone (public content) | none |
| Build pipeline / dedicated server needing hidden content (e.g. Umbra) | DRF token for a service account holding `core.view_hidden_content` (e.g. Narrative Editor role). Create the account in Team & roles, then `POST /api/v1/auth/token/`. Store the token in CI secrets. |
| Future player client | Player signs in: `POST /api/v1/auth/token/` with email and password → `Authorization: Token <key>`. Player endpoints: `GET /me/`, `GET /me/quests/{slug}/`, `POST /me/quests/{slug}/start/`. |

**Never place a privileged token in a distributed game client.** Anything shipped can be extracted.

## Trust model

- The client is untrusted. Quest state changes go through server functions (`apps/quests/services.py`) that check publication, prerequisites, start conditions, objective progress and completion conditions.
- Only `start` is exposed today. Objective progress, rewards, inventory and any competitive state need dedicated, server-validated endpoints (and anti-cheat design) before online play.
- Rate limits: 120 requests/minute anonymous, 600/minute authenticated; token issuance 10 per 15 minutes per IP.
