# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings


class CalendarWidget(forms.TextInput):
    '''
    Данный виджет является, практически, копией
    django.contrib.admin.widgets.AdminDateWidget
    Но наследование от AdminDateWidget не удалось из-за неверного
    порядка JS-файлов в результирующем html, при наследовании.

    Для работы необходимо в urls.py добавить:
    (r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog'),
    '''
    class Media:
        js = ('/admin/jsi18n/',
              settings.STATIC_URL + 'admin/js/core.js',
              settings.STATIC_URL + "admin/js/calendar.js",
              settings.STATIC_URL + "admin/js/admin/DateTimeShortcuts.js")
        css = {
            'all': (
                settings.STATIC_URL + 'admin/css/forms.css',
                settings.STATIC_URL + 'admin/css/widgets.css',)
        }

    def __init__(self, attrs={}):
        super(CalendarWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'})
