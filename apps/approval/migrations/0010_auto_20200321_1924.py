# Generated by Django 2.2.11 on 2020-03-21 18:24

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0045_auto_20200222_1436"),
        ("approval", "0009_auto_20200229_1046"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommitteeApplicationPeriod",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=128, verbose_name="Tittel")),
                ("start", models.DateTimeField(verbose_name="Starttid")),
                ("deadline", models.DateTimeField(verbose_name="First")),
                (
                    "deadline_delta",
                    models.DurationField(
                        default=datetime.timedelta(1),
                        help_text="Hvor lenge etter fristen skal det være mulig å søke?",
                        verbose_name="Slingringsmonn",
                    ),
                ),
                (
                    "committees",
                    models.ManyToManyField(
                        related_name="application_periods",
                        to="authentication.OnlineGroup",
                        verbose_name="Komiteer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Opptaksperiode",
                "verbose_name_plural": "Opptaksperioder",
                "ordering": ("-start", "-deadline"),
            },
        ),
        migrations.AddField(
            model_name="committeeapplication",
            name="application_period",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="applications",
                to="approval.CommitteeApplicationPeriod",
                verbose_name="Opptaksperiode",
            ),
        ),
    ]
