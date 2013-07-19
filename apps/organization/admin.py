#coding: utf8
from django.contrib import admin

from models import Organization

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'ldap_name')
    search_fields = ('name',)

admin.site.register(Organization, OrganizationAdmin)
