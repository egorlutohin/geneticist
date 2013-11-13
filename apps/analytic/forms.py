#coding: utf8
from django import forms

from patient.models import Patient


class PeriodForm(forms.Form):
    period_start = forms.DateField(label=u'Период начала')
    period_end = forms.DateField(label=u'Период окончания')
    TYPE_RESIDENCES = (('', '-----',),) + Patient.TYPE_RESIDENCES
    type_residence = forms.ChoiceField(required=False,
                                       label=u'Место проживания',
                                       choices=TYPE_RESIDENCES)

    def clean(self):
        cd = self.cleaned_data
        period_start = cd.get('period_start')
        period_end = cd.get('period_end')
        if not None in (period_start, period_end,):
            if period_start > period_end:
                text = u'''Дата начала периода должна быть меньше или равной
                           дате окончания периода'''
                raise forms.ValidationError(text)
        return cd
