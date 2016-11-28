# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-18 08:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0010_auto_20161116_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secondaryeducationexam',
            name='result',
            field=models.CharField(blank=True, choices=[('LOW', 'Moins de 65%'), ('MIDDLE', 'entre 65% et 75%'), ('HIGH', 'plus de 75%'), ('NO_RESULT', 'pas encore de résultat'), ('SUCCEED', 'succeeded'), ('FAILED', 'failed'), ('ENROLLMENT_IN_PROGRESS', 'demanded_result')], max_length=30, null=True),
        ),
    ]