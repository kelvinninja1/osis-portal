# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-04-06 07:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam_enrollment', '0007_auto_20180406_0836'),
    ]

    operations = [
        migrations.AddField(
            model_name='examenrollmentrequest',
            name='fetch_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
