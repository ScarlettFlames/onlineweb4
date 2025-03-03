# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

User = settings.AUTH_USER_MODEL

DURATION = 20
# summer starts 1st June, ends 15th August
SUMMER = ((6, 1), (8, 15))
# winter starts 1st December, ends 15th January
WINTER = ((12, 1), (1, 15))


def get_expiration_date(user):
    if user:
        marks = MarkUser.objects.filter(user=user).order_by("-expiration_date")
        if marks:
            return marks[0].expiration_date
    return None


class MarksManager(models.Manager):
    @staticmethod
    def all_active():
        return Mark.objects.filter(given_to__expiration_date__gt=timezone.now().date())

    @staticmethod
    def active(user):
        return MarkUser.objects.filter(user=user).filter(
            expiration_date__gt=timezone.now().date()
        )

    @staticmethod
    def inactive(user=None):
        return MarkUser.objects.filter(user=user).filter(
            expiration_date__lte=timezone.now().date()
        )


class Mark(models.Model):
    CATEGORY_CHOICES = (
        (0, _("Ingen")),
        (1, _("Sosialt")),
        (2, _("Bedriftspresentasjon")),
        (3, _("Kurs")),
        (4, _("Tilbakemelding")),
        (5, _("Kontoret")),
        (6, _("Betaling")),
    )

    title = models.CharField(_("tittel"), max_length=155)
    added_date = models.DateField(_("utdelt dato"))
    given_by = models.ForeignKey(
        User,
        related_name="mark_given_by",
        verbose_name=_("gitt av"),
        editable=False,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    last_changed_date = models.DateTimeField(
        _("sist redigert"), auto_now=True, editable=False
    )
    last_changed_by = models.ForeignKey(
        User,
        related_name="marks_last_changed_by",
        verbose_name=_("sist redigert av"),
        editable=False,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
    )
    description = models.CharField(
        _("beskrivelse"),
        max_length=255,
        help_text=_(
            "Hvis dette feltet etterlates blankt vil det fylles med en standard grunn for typen prikk som er valgt."
        ),
        blank=True,
    )
    category = models.SmallIntegerField(
        _("kategori"), choices=CATEGORY_CHOICES, default=0
    )

    # managers
    objects = models.Manager()  # default manager
    marks = MarksManager()  # active marks manager

    def __str__(self):
        return _("Prikk for %s") % self.title

    def save(self, *args, **kwargs):
        if not self.added_date:
            self.added_date = timezone.now().date()
        super().save(*args, **kwargs)

    def delete(self, **kwargs):
        given_to = [mu.user for mu in self.given_to.all()]
        super().delete()
        for user in given_to:
            _fix_mark_history(user)

    class Meta:
        verbose_name = _("Prikk")
        verbose_name_plural = _("Prikker")
        permissions = (("view_mark", "View Mark"),)
        default_permissions = ("add", "change", "delete")


class MarkUser(models.Model):
    """
    One entry for a user that has received a mark.
    """

    mark = models.ForeignKey(Mark, related_name="given_to", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    expiration_date = models.DateField(_("utløpsdato"), editable=False)

    def save(self, *args, **kwargs):
        run_history_update = False
        if not self.expiration_date:
            self.expiration_date = timezone.now().date()
            run_history_update = True
        super().save(*args, **kwargs)
        if run_history_update:
            _fix_mark_history(self.user)

    def delete(self):
        super().delete()
        _fix_mark_history(self.user)

    def __str__(self):
        return _("Mark entry for user: %s") % self.user.get_full_name()

    class Meta:
        unique_together = ("user", "mark")
        ordering = ("expiration_date",)
        permissions = (("view_userentry", "View UserEntry"),)
        default_permissions = ("add", "change", "delete")


def _fix_mark_history(user):
    """
    Goes through a users complete mark history and resets all expiration dates.

    The reasons for doing it this way is that the mark rules now insist on marks building
    on previous expiration dates if such exists. Instead of having the entire mark database
    be a linked list structure, it can be simplified to guarantee the integrity of the
    expiration dates by running this whenever;

     * new Mark is saved or deleted
     * a new MarkUser entry is made
     * an existing MarkUser entry is deleted
    """
    markusers = MarkUser.objects.filter(user=user).order_by("mark__added_date")
    last_expiry_date = None
    for entry in markusers:

        # If the creation date is before the 1 of february 2022, the duration of the
        # mark should be 30 days. The mark rule duration was changed.
        duration = DURATION
        mark_change_date = date(2022, 2, 1)
        if entry.mark.added_date < mark_change_date:
            duration = 30

        # If there's a last_expiry date, it means a mark has been processed already.
        # If that expiration date is within a DURATION of this added date, build on it.
        if (
            last_expiry_date
            and entry.mark.added_date - timedelta(days=duration) < last_expiry_date
        ):
            entry.expiration_date = _get_with_duration_and_vacation(last_expiry_date)
        # If there is no last_expiry_date or the last expiry date is over a DURATION old
        # we add DURATIION days from the added date of the mark.
        else:
            entry.expiration_date = _get_with_duration_and_vacation(
                entry.mark.added_date
            )
        entry.save()
        last_expiry_date = entry.expiration_date


def _get_with_duration_and_vacation(added_date=timezone.now()):
    """
    Checks whether the span of a marks duration needs to have vacation durations added.
    """

    duration = DURATION
    mark_change_date = date(2022, 2, 1)
    if added_date < mark_change_date:
        duration = 30

    if type(added_date) == datetime:
        added_date = added_date.date()

    # Add the duration
    expiry_date = added_date + timedelta(days=duration)
    # Set up the summer and winter vacations
    summer_start_date = date(added_date.year, SUMMER[0][0], SUMMER[0][1])
    summer_end_date = date(added_date.year, SUMMER[1][0], SUMMER[1][1])
    first_winter_start_date = date(added_date.year, WINTER[0][0], WINTER[0][1])
    first_winter_end_date = date(added_date.year + 1, WINTER[1][0], WINTER[1][1])
    second_winter_end_date = date(added_date.year, WINTER[1][0], WINTER[1][1])

    # If we're in the middle of summer, add the days remaining of summer
    if summer_start_date < added_date < summer_end_date:
        expiry_date += timedelta(days=(summer_end_date - added_date).days)
    # If the number of days between added_date and the beginning of summer vacation is less
    # than the duration, we need to add the length of summer to the expiry date
    elif 0 < (summer_start_date - added_date).days < duration:
        expiry_date += timedelta(days=(summer_end_date - summer_start_date).days)
    # Same for middle of winter vacation, which will be at the end of the year
    elif first_winter_start_date < added_date < first_winter_end_date:
        expiry_date += timedelta(days=(first_winter_end_date - added_date).days)
    # And for before the vacation
    elif 0 < (first_winter_start_date - added_date).days < duration:
        expiry_date += timedelta(
            days=(first_winter_end_date - first_winter_start_date).days
        )
    # Then we need to check the edge case where now is between newyears and and of winter vacation
    elif second_winter_end_date > added_date:
        expiry_date += timedelta(days=(second_winter_end_date - added_date).days)

    return expiry_date


class Suspension(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(_("tittel"), max_length=64)
    description = models.CharField(_("beskrivelse"), max_length=255)
    active = models.BooleanField(default=True)
    added_date = models.DateTimeField(auto_now=True, editable=False)
    expiration_date = models.DateField(_("utløpsdato"), null=True, blank=True)

    # Using id because foreign key to Payment caused circular dependencies
    payment_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "Suspension: " + str(self.user)

    class Meta:
        default_permissions = ("add", "change", "delete")

    # TODO URL


class MarkRuleSet(models.Model):
    """
    A version of the mark rules set by Linjeforeningen Online
    """

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    valid_from_date = models.DateTimeField(auto_now_add=True)
    """ Rules written in markdown """
    content = models.TextField(
        verbose_name="Regler", help_text="Regelsett skrevet i markdown"
    )
    version = models.CharField(max_length=128, verbose_name="Versjon", unique=True)

    @classmethod
    def get_current_rule_set(cls) -> "MarkRuleSet":
        """
        The latest set of mark rules which have become active
        """
        return (
            cls.objects.order_by("-valid_from_date")
            .exclude(valid_from_date__gt=timezone.now())
            .first()
        )

    @classmethod
    def has_user_accepted_mark_rules(cls, user: User) -> bool:
        current_rules = cls.get_current_rule_set()
        return RuleAcceptance.objects.filter(user=user, rule_set=current_rules).exists()

    @classmethod
    def accept_mark_rules(cls, user: User):
        current_rules = cls.get_current_rule_set()
        if not cls.has_user_accepted_mark_rules(user):
            RuleAcceptance.objects.create(user=user, rule_set=current_rules)

    def __str__(self):
        return self.version

    class Meta:
        verbose_name = "Prikkegelsett"
        verbose_name_plural = "Prikkeregelsett"
        ordering = ("-valid_from_date",)


class RuleAcceptance(models.Model):
    user = models.ForeignKey(
        to=User,
        related_name="accepted_mark_rule_sets",
        verbose_name="Godkjente prikkeregelsett",
        on_delete=models.CASCADE,
        editable=False,
    )
    rule_set = models.ForeignKey(
        to=MarkRuleSet,
        related_name="user_accepts",
        verbose_name="Brukere som har akseptert",
        on_delete=models.CASCADE,
        editable=False,
    )
    accepted_date = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.rule_set} - {self.user}"

    class Meta:
        verbose_name = "Regelgodkjenning"
        verbose_name_plural = "Regelgodkjennelser"
        unique_together = (("user", "rule_set"),)
        ordering = ("rule_set", "accepted_date")
