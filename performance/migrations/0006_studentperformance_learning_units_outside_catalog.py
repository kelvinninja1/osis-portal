# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-11-09 10:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0005_studentperformance_courses_registration_validated'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentperformance',
            name='learning_units_outside_catalog',
            field=models.NullBooleanField(),
        ),
    ]
