#coding: utf8
from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from mkb.models import Mkb

admin.site.register(Mkb, MPTTModelAdmin)
