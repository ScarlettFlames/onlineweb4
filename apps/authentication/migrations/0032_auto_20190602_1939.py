# Generated by Django 2.1.8 on 2019-06-02 17:39

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0031_auto_20190506_1719")]

    operations = [
        migrations.AddField(
            model_name="position",
            name="period_end",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name="position",
            name="period_start",
            field=models.DateField(default=datetime.date.today),
        ),
    ]
