#coding: utf8
from django import forms

from patient.forms import SearchForm
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


class MkbForm(SearchForm):
    """ Форма для отчета заболеваний МКБ за период """
    def __init__(self, *args, **kwargs):
        super(MkbForm, self).__init__(*args, **kwargs)
        self.fields['full_name'].required = True
        self.fields['diagnosis'].required = True

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '')
        parts = [p for p in full_name.split(' ') if p.strip()]
        if len(parts) != 3:
            raise forms.ValidationError(u'Нужно ввести фамилию, имя и отчество пациента')
        return full_name
