# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-02 07:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0006_auto_20170301_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipstudentinformation',
            name='contest',
            field=models.CharField(choices=[('SPECIALIST', 'specialist'), ('GENERALIST', 'generalist')], default='GENERALIST', max_length=124),
        ),
    ]
