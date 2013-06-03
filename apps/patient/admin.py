#coding: utf8
from django.contrib import admin

from models import Patient, Visit, Diagnosis


class QsMixin(object):
    def queryset(self, request):
        qs = self.model.all_objects.get_query_set()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class VisitInline(QsMixin, admin.TabularInline):
    model = Visit


class DiagnosisInline(QsMixin, admin.StackedInline):
    model = Diagnosis


class PatientAdmin(QsMixin, admin.ModelAdmin):
    list_display = list_display_links = ('full_name', 'birthday',
                                         'diagnosis_text', 'allocate_lpu',
                                         'get_gender_display',)
    search_fields = ['full_name']
    list_filter = ['special_cure']
    inlines = [VisitInline, DiagnosisInline]


admin.site.register(Patient, PatientAdmin)
