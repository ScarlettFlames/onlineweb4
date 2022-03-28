# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.offline.models import Issue
from apps.offline.tasks import create_thumbnail_task
from utils.disable_for_loaddata import disable_for_loaddata


@receiver(post_save, sender=Issue)
@disable_for_loaddata
def trigger_create_thumbnail(sender, instance: Issue, created=False, **kwargs):
    """
    Calls the create thumbnail task if an issue saved (either created or updated).
    """
    if not instance.image:
        create_thumbnail_task(issue_id=instance.id)
