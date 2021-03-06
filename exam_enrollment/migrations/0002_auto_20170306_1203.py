# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-06 11:03
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam_enrollment', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExamEnrollment',
            new_name='ExamEnrollmentSubmitted',
        ),
        migrations.RemoveField(
            model_name='examenrollmentsubmitted',
            name='offer_year_acronym',
        ),
        migrations.RemoveField(
            model_name='examenrollmentsubmitted',
            name='registration_id',
        ),
        migrations.AddField(
            model_name='examenrollmentsubmitted',
            name='offer_enrollment',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='base.OfferEnrollment'),
        ),
        migrations.CreateModel(
            name='ExamEnrollmentForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_enrollment', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='base.OfferEnrollment')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('form', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),

    ]


