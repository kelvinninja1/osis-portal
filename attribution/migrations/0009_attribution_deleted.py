# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-10 12:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0008_auto_20170228_0848'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
