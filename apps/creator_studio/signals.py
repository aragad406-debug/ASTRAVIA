from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def sync_studio_roles(sender, **kwargs):
    """Keep studio role groups in sync. Runs once per migrate, after the last app with models
    (by then Django has created every permission)."""
    model_apps = [config for config in apps.get_app_configs() if config.models_module is not None]
    if not model_apps or sender.name != model_apps[-1].name:
        return
    from .roles import sync_roles

    sync_roles(verbosity=kwargs.get("verbosity", 0) > 1)
