# Generated by Django 3.2.12 on 2022-04-03 18:38

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("companyprofile", "0001_initial"),
        ("companyprofile", "0002_auto_20151014_2132"),
        ("companyprofile", "0003_company_image"),
        ("companyprofile", "0004_auto_20160413_2328"),
        ("companyprofile", "0005_auto_20170130_2037"),
        ("companyprofile", "0006_auto_20190506_1719"),
        ("companyprofile", "0007_company_created_date"),
    ]

    initial = True

    dependencies = [
        ("gallery", "0003_auto_20151015_0010"),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
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
                ("name", models.CharField(max_length=100, verbose_name="bedriftsnavn")),
                (
                    "short_description",
                    models.TextField(verbose_name="kort beskrivelse"),
                ),
                (
                    "long_description",
                    models.TextField(
                        blank=True, null=True, verbose_name="utdypende beskrivelse"
                    ),
                ),
                ("site", models.CharField(max_length=100, verbose_name="hjemmeside")),
                (
                    "email_address",
                    models.EmailField(
                        blank=True,
                        max_length=75,
                        null=True,
                        verbose_name="epostaddresse",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="telefonnummer",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gallery.responsiveimage",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Opprettet dato",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bedrift",
                "verbose_name_plural": "Bedrifter",
                "permissions": (("view_company", "View Company"),),
                "ordering": ("name",),
                "default_permissions": ("add", "change", "delete"),
            },
        ),
    ]
