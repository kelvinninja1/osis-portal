# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-04 13:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0006_auto_20170320_0811'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gradetype',
            name='language_exam_required',
        ),
    ]
