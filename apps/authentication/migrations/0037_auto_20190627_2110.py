# Generated by Django 2.1.9 on 2019-06-27 19:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0036_auto_20190627_1855")]

    operations = [
        migrations.AlterField(
            model_name="onlinegroup",
            name="email",
            field=models.EmailField(blank=True, max_length=128, verbose_name="E-post"),
        ),
        migrations.AlterField(
            model_name="onlinegroup",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="online_groups",
                to="gallery.ResponsiveImage",
            ),
        ),
    ]
