# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-19 08:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0041_auto_20181017_1540'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='learningunityear',
            unique_together=set([('acronym', 'academic_year'), ('learning_unit', 'academic_year')]),
        ),
    ]
