##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db import models
from django.contrib import admin
from base.enums.organization_type import TYPES as ORGANIZATION_TYPES


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'website', 'prefix', 'type')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'prefix', 'website', 'type')}),)
    search_fields = ['acronym']


class Organization(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    acronym = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    prefix = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True, choices=ORGANIZATION_TYPES, default='UNKNOWN')
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


def find_by_id(organization_id):
    return Organization.objects.get(pk=organization_id)


def search(acronym=None, name=None, type=None, prefix=None):
    out = None
    queryset = Organization.objects

    if acronym:
        queryset = queryset.filter(acronym=acronym)

    if name:
        queryset = queryset.filter(name=name)

    if type:
        queryset = queryset.filter(type=type)

    if prefix:
        queryset = queryset.filter(prefix=prefix)

    if acronym or name or type or prefix:
        out = queryset

    return out
