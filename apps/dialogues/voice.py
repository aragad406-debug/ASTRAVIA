"""Text-to-speech provider interface.

No provider ships enabled. To add one, subclass VoiceProvider, implement `synthesize()` so it returns
audio bytes and a MIME type (or raises VoiceProviderError), and register it in PROVIDERS. API keys are
read from the environment on the server and are never sent to the browser.
"""
import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import VoiceGenerationRequest

logger = logging.getLogger("astravia.voice")


class VoiceProviderError(Exception):
    pass


class VoiceProvider:
    name = "base"

    def __init__(self, api_key):
        self.api_key = api_key

    def synthesize(self, *, text, voice_id, language, speaking_rate, pitch_semitones):  # pragma: no cover - interface
        raise NotImplementedError


PROVIDERS: dict[str, type[VoiceProvider]] = {}


def configured_provider():
    name = (settings.VOICE_PROVIDER or "").strip().lower()
    if not name or not settings.VOICE_PROVIDER_API_KEY:
        return None
    cls = PROVIDERS.get(name)
    return cls(settings.VOICE_PROVIDER_API_KEY) if cls else None


def request_generation(dialogue, voice_profile, language, user):
    """Create a generation request. Without a configured provider the request is recorded as
    'not configured' — it is never reported as successful."""
    from apps.media_library.models import MediaAsset

    text = dialogue.text_ar if language == "ar" else dialogue.text_en
    req = VoiceGenerationRequest.objects.create(
        dialogue=dialogue, voice_profile=voice_profile, language=language, text=text or "", requested_by=user,
        provider=settings.VOICE_PROVIDER or "",
    )
    if not text:
        req.status, req.error_message = VoiceGenerationRequest.Status.FAILED, "This line has no text in that language."
        req.save(update_fields=["status", "error_message"])
        return req
    provider = configured_provider()
    if provider is None or voice_profile.provider != voice_profile.Provider.EXTERNAL:
        req.status = VoiceGenerationRequest.Status.NOT_CONFIGURED
        req.error_message = (
            "No text-to-speech provider is configured (VOICE_PROVIDER / VOICE_PROVIDER_API_KEY), or this voice profile "
            "is set to manual upload. Upload recorded audio instead."
        )
        req.save(update_fields=["status", "error_message"])
        return req
    try:
        audio, mime = provider.synthesize(
            text=text, voice_id=voice_profile.provider_voice_id, language=language,
            speaking_rate=float(voice_profile.speaking_rate), pitch_semitones=voice_profile.pitch_semitones,
        )
        ext = {"audio/mpeg": "mp3", "audio/ogg": "ogg", "audio/wav": "wav"}.get(mime, "bin")
        asset = MediaAsset(
            title=f"{dialogue.key} ({language}) — generated", kind=MediaAsset.Kind.AUDIO, role=MediaAsset.Role.VOICE,
            is_generated=True, uploaded_by=user, mime_type=mime, size_bytes=len(audio),
        )
        asset.file.save(f"{dialogue.key}-{language}.{ext}", ContentFile(audio), save=False)
        asset.save()
        req.result_asset = asset
        req.status = VoiceGenerationRequest.Status.SUCCEEDED
        req.completed_at = timezone.now()
    except VoiceProviderError as exc:
        req.status = VoiceGenerationRequest.Status.FAILED
        req.error_message = str(exc)[:500]
    except Exception:  # never leak provider internals to the UI
        logger.exception("Voice generation failed")
        req.status = VoiceGenerationRequest.Status.FAILED
        req.error_message = "The provider request failed. Details are in the server log."
    req.save()
    return req
