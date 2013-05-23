#coding: utf8
from django.contrib import admin

from models import Patient, Visit, Diagnosis


class VisitInline(admin.TabularInline):
    model = Visit


class DiagnosisInline(admin.StackedInline):
    model = Diagnosis


class PatientAdmin(admin.ModelAdmin):
    list_display = list_display_links = ('full_name', 'birthday',
                                         'diagnosis_text', 'allocate_lpu',
                                         'get_gender_display',)
    search_fields = ['full_name']
    list_filter = ['special_cure']


admin.site.register(Patient, PatientAdmin)
