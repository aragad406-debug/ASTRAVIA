# Database design

PostgreSQL in production (SQLite supported for local development and tests). All primary keys are `BigAutoField`. Localized text uses paired `_en` / `_ar` columns.

## Shared columns (abstract models)

| Mixin | Columns |
|---|---|
| `TimeStampedModel` | `created_at`, `updated_at` |
| `PublishableModel` | `status` (indexed), `publish_at`, `published_at`, `revision`, `is_seeded` |
| `VisibilityModel` | `visibility` ∈ public / teaser / hidden (indexed) |
| `SearchableModel` | `search_document` (normalized text) |

## Entities

| Model | Key fields and relations | Constraints |
|---|---|---|
| `accounts.User` | `email` (login), `email_verified` | unique email |
| `accounts.UserProfile` | 1:1 user; display name, language, avatar, privacy | |
| `accounts.AccountDeletionRequest` | user (SET_NULL), email snapshot, status, processed_by | one pending request per user |
| `core.SiteConfiguration` | homepage copy, trailer, ambient audio, contact, social links; holds custom permissions | singleton (`id = 1` check) |
| `core.Page` | slug, title, body, footer flag | unique slug |
| `core.UIString` | key, overrides | unique key |
| `core.ContentRevision` | generic FK, revision number, JSON snapshot, author | unique (type, object, number) |
| `core.PublicationRecord` | generic FK, action, from/to status, actor | indexed by object |
| `core.AuditEvent` | actor (SET_NULL) + label, action, generic target, summary, IP | indexed action, created_at |
| `core.NewsletterSubscriber` | email, language | unique email |
| `media_library.MediaAsset` | kind, role, file or external URL / Unreal path, alt text, detected format, size, dimensions, generated flag, archived | external assets need a reference |
| `worlds.World` | slug, order, names, descriptions, capital, `ruler` → Character (SET_NULL), theme, colours (hex-validated), hero image, video, Unreal level, unlock conditions | unique slug |
| `worlds.Region` | world, slug, kind, secret flag, unlock conditions | unique (world, slug) |
| `characters.Character` | slug, category, world, biography fields, secrets (studio-only), ages, colour, portrait, gallery M2M, 3D/skeletal/animation refs | unique slug |
| `characters.CharacterRelationship` | from, to, kind, description, secret | unique (from, to, kind); from ≠ to; no circular parent |
| `narrative.StoryArc` | slug, type, world, characters M2M | unique slug |
| `narrative.StoryChapter` | arc, slug, order, type, body, closing line, world, characters, prerequisite quests, required lore, unlock conditions, ending type, spoiler | unique (arc, slug), unique (arc, order) |
| `narrative.StoryNode` | chapter, key, type, start flag, text, speaker, dialogue, cinematic, ending type | unique (chapter, key); one start per chapter (partial unique) |
| `narrative.StoryBranch` | from node, to node, label, condition, consequences | no self-loop; same arc (validated) |
| `narrative.LoreEntry` | slug, type, content, worlds/characters/quests/chapters M2M, related entries (symmetric), discovery conditions, timeline position, importance | unique slug |
| `narrative.Artifact` | slug, rarity, key item, world, lore, icon, Unreal item id | unique slug |
| `narrative.Cinematic` | slug, chapter, characters, Unreal sequence, duration, trigger conditions, render status, rendered video | rendered ⇒ video present |
| `narrative.CinematicScene` | cinematic, order, shot, camera, dialogue, voice track, subtitles, music, SFX | |
| `quests.Quest` | slug, type, world, giver, characters, start/completion/failure conditions, required items, cinematics, lore unlocked, repeatable | unique slug |
| `quests.QuestObjective` | quest, key, type, target, count, optional, condition | unique (quest, key); count ≥ 1 |
| `quests.QuestDependency` | quest, requires (PROTECT), requirement | unique pair; not self; cycle check in `clean()` |
| `quests.QuestReward` | quest, type, artifact/lore (PROTECT), amount | item ⇒ artifact; lore ⇒ lore entry |
| `quests.PlayerQuestState` | user, quest, state, objective progress, timestamps | unique (user, quest) |
| `quests.BossEncounter` | slug, boss/world (PROTECT), arena, cinematics, required quest/state, health bar, conditions, rewards | unique slug |
| `quests.BossPhase` | encounter, order, threshold %, dialogue trigger, environment | unique (encounter, order); threshold ≤ 100 |
| `dialogues.DialogueEntry` | key, speaker, guide, category, text, world, quest, trigger event, page context, conditions, emotion, delivery notes, duration, priority, voice EN/AR | unique key |
| `dialogues.DialogueChoice` | entry, text, next entry, condition, consequences | next ≠ entry |
| `dialogues.GuideAssistant` | 1:1 character (PROTECT), purpose, intro, voice profile, languages, worlds, trigger pages, position, primary, unlock conditions, AI flag | one primary guide |
| `dialogues.VoiceProfile` | character, provider, voice id, language, rate, pitch | unique slug |
| `dialogues.VoiceGenerationRequest` | dialogue, profile, language, status, error, result asset | |
| `localization.GlossaryTerm` | term EN/AR, category, notes | unique English term |
| `localization.TranslationReview` | generic FK, field, fingerprint of both texts | unique (object, field) |
| `announcements.Announcement` | slug, category, title/summary/body, cover, pinned | unique slug |

## Deletion behaviour

- Narrative links from content to optional context use `SET_NULL`; structural children (regions, objectives, nodes, scenes, phases, choices) `CASCADE` with their parent.
- Records others depend on structurally use `PROTECT` (dependency targets, reward artifacts/lore, boss character/world, guide character).
- The studio only deletes drafts/archived records with no linked content; otherwise it tells the editor to archive.

## Migrations

Generated by Django (`apps/*/migrations`). Don't edit applied migrations; add new ones. Never reset the production database to fix a migration — write a corrective migration.
