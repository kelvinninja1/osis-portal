# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-27 09:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssimilationCriteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criteria', models.CharField(max_length=255, unique=True)),
                ('order', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iso_code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(max_length=80, unique=True)),
                ('nationality', models.CharField(blank=True, max_length=80, null=True)),
                ('european_union', models.BooleanField(default=False)),
                ('dialing_code', models.CharField(blank=True, max_length=3, null=True)),
                ('cref_code', models.CharField(blank=True, max_length=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EducationInstitution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('institution_type', models.CharField(choices=[('SECONDARY', 'Secondaire'), ('UNIVERSITY', 'University'), ('HIGHER_NON_UNIVERSITY', 'Higher non-university')], max_length=25)),
                ('postal_code', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=255)),
                ('national_community', models.CharField(blank=True, choices=[('FRENCH', 'Communauté française de Belgique'), ('GERMAN', 'Communauté germanophone'), ('DUTCH', 'Communauté flamande')], max_length=20, null=True)),
                ('adhoc', models.BooleanField(default=False)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Country')),
            ],
        ),
        migrations.CreateModel(
            name='EducationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('TRANSITION', 'Transition'), ('QUALIFICATION', 'Qualification'), ('ANOTHER', 'Autre')], max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('adhoc', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GradeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=255)),
                ('grade', models.CharField(choices=[('BACHELOR', 'bachelor'), ('MASTER', 'master'), ('DOCTORATE', 'ph_d'), ('TRAINING_CERTIFICATE', 'teacher_training_certificate'), ('CERTIFICATE', 'certificate')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4, unique=True)),
                ('name', models.CharField(max_length=80, unique=True)),
                ('recognized', models.BooleanField(default=False)),
            ],
        ),
    ]
