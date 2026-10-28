"""Studio roles are Django Groups kept in sync with this definition after every migrate."""

CONTENT_MODELS = {
    "worlds": ["world", "region"],
    "characters": ["character", "characterrelationship"],
    "narrative": ["storyarc", "storychapter", "storynode", "storybranch", "loreentry", "artifact", "cinematic", "cinematicscene"],
    "quests": ["quest", "questobjective", "questdependency", "questreward", "bossencounter", "bossphase"],
    "dialogues": ["dialogueentry", "dialoguechoice", "guideassistant", "voiceprofile", "voicegenerationrequest"],
    "media_library": ["mediaasset"],
    "announcements": ["announcement"],
    "localization": ["glossaryterm", "translationreview"],
    "core": ["page", "uistring", "siteconfiguration"],
}


def _model_perms(app, models, actions):
    return [f"{app}.{action}_{model}" for model in models for action in actions]


def _all_view():
    perms = []
    for app, models in CONTENT_MODELS.items():
        perms += _model_perms(app, models, ["view"])
    return perms + ["core.access_studio"]


def _full(app, models=None):
    return _model_perms(app, models or CONTENT_MODELS[app], ["add", "change", "delete", "view"])


def _all_full():
    perms = []
    for app in CONTENT_MODELS:
        perms += _full(app)
    return perms


LOCALIZED_CHANGE = _model_perms("worlds", ["world", "region"], ["change"]) + _model_perms(
    "characters", ["character", "characterrelationship"], ["change"]
) + _model_perms("narrative", CONTENT_MODELS["narrative"], ["change"]) + _model_perms(
    "quests", ["quest", "questobjective", "questreward", "bossencounter", "bossphase"], ["change"]
) + _model_perms("dialogues", ["dialogueentry", "dialoguechoice", "guideassistant"], ["change"]) + _model_perms(
    "announcements", ["announcement"], ["change"]
) + _model_perms("core", ["page", "uistring", "siteconfiguration"], ["change", "add"]) + _model_perms(
    "media_library", ["mediaasset"], ["change"]
)

ROLES = {
    "Owner": None,  # superuser: every permission
    "Administrator": _all_full() + [
        "core.access_studio", "core.publish_content", "core.review_content", "core.view_hidden_content", "core.manage_team",
        "core.view_audit_log", "core.manage_site_settings",
    ],
    "Narrative Editor": _all_view() + _full("narrative") + _model_perms(
        "dialogues", ["dialogueentry", "dialoguechoice"], ["add", "change", "view"]
    ) + ["core.view_hidden_content"],
    "World Designer": _all_view() + _full("worlds") + ["core.view_hidden_content"],
    "Character Editor": _all_view() + _full("characters") + _model_perms(
        "dialogues", ["guideassistant"], ["add", "change", "view"]
    ) + ["core.view_hidden_content"],
    "Quest Designer": _all_view() + _full("quests") + _model_perms("narrative", ["artifact"], ["add", "change"]) + ["core.view_hidden_content"],
    "Localization Editor": _all_view() + LOCALIZED_CHANGE + _full("localization") + ["core.view_hidden_content"],
    "Voice Editor": _all_view() + _model_perms("dialogues", ["voiceprofile", "voicegenerationrequest"], ["add", "change", "view"])
    + _model_perms("dialogues", ["dialogueentry"], ["change"]) + _model_perms("media_library", ["mediaasset"], ["add", "change"]),
    "Media Editor": _all_view() + _full("media_library"),
    "Reviewer": _all_view() + ["core.review_content", "core.publish_content", "core.view_hidden_content"],
    "Read-Only Viewer": _all_view(),
}


def sync_roles(verbosity=0):
    from django.contrib.auth.models import Group, Permission

    perm_index = {
        f"{p.content_type.app_label}.{p.codename}": p for p in Permission.objects.select_related("content_type")
    }
    missing = set()
    for name, codes in ROLES.items():
        group, _ = Group.objects.get_or_create(name=name)
        if codes is None:
            codes = list(perm_index)
        perms = []
        for code in sorted(set(codes)):
            if code in perm_index:
                perms.append(perm_index[code])
            else:
                missing.add(code)
        group.permissions.set(perms)
    if missing and verbosity:
        print("Role sync skipped unknown permissions:", ", ".join(sorted(missing)))
    return missing
