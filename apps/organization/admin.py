#coding: utf8
from django.contrib import admin

from models import Organization

admin.site.register(Organization, admin.ModelAdmin)
