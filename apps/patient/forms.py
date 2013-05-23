#coding: utf8
from django import forms
from django.forms.models import inlineformset_factory

from models import Patient, Visit, Diagnosis


class SearchForm(forms.Form):
    """ Форма поиска пациентов """
    full_name = forms.CharField(max_length=300, required=False)
    special_cure = forms.ChoiceField(choices=Patient.SPECIAL_CURES,
                                     required=False)
    birthday = forms.DateField(required=False)


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis


VisitFormset = inlineformset_factory(Patient, Visit, extra=1, form=VisitForm)


DiagnosisFormset = inlineformset_factory(Patient, Diagnosis,
                                         extra=1, form=DiagnosisForm)
