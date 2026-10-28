"""Promote scheduled content whose publication time has arrived. Run on a schedule (e.g. a Render cron job).

Public pages already treat due scheduled content as live; this command keeps stored status accurate."""
from django.core.management.base import BaseCommand

from apps.core.publishing import promote_due_scheduled
from apps.creator_studio.registry import publishable_models


class Command(BaseCommand):
    help = "Publish scheduled content whose publish time has passed."

    def handle(self, *args, **opts):
        count = promote_due_scheduled(publishable_models())
        self.stdout.write(self.style.SUCCESS(f"{count} scheduled item(s) published."))
