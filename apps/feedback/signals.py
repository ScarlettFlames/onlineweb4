from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from utils.disable_for_loaddata import disable_for_loaddata

from .models import FeedbackRelation, GenericSurvey, RegisterToken


@receiver(signal=post_save, sender=GenericSurvey)
@disable_for_loaddata
def sync_survey_options_to_feedback_relation(sender, instance: GenericSurvey, **kwargs):
    try:
        feedback_relation = instance.get_feedback_relation()
        feedback_relation.feedback = instance.feedback
        feedback_relation.deadline = instance.deadline
        feedback_relation.save()
    except FeedbackRelation.DoesNotExist:
        FeedbackRelation.objects.create(
            content_type=ContentType.objects.get_for_model(GenericSurvey),
            content_object=instance,
            object_id=instance.id,
            feedback=instance.feedback,
            deadline=instance.deadline,
            gives_mark=False,
        )


@receiver(signal=post_save, sender=GenericSurvey)
@disable_for_loaddata
def handle_generic_survey_permissions(sender, instance: GenericSurvey, **kwargs):
    survey_owner_permissions = [
        "feedback.view_genericsurvey",
        "feedback.change_genericsurvey",
        "feedback.delete_genericsurvey",
    ]
    for permission in survey_owner_permissions:
        assign_perm(permission, instance.owner, obj=instance)
        if instance.owner_group:
            assign_perm(permission, instance.owner_group, obj=instance)


@receiver(signal=post_save, sender=FeedbackRelation)
@disable_for_loaddata
def create_feedback_relation_token(sender, instance: FeedbackRelation, **kwargs):
    if not instance.token_objects.exists():
        RegisterToken.objects.create(fbr=instance)
