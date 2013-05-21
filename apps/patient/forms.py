#coding: utf8
from django import forms
from django.forms.models import inlineformset_factory

from models import Patient, Visit, Diagnosis


class PatienForm(forms.ModelForm):
    class Meta:
        model = Patient


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis


VisitFormset = inlineformset_factory(Patient, Visit, extra=1, form=VisitForm)


DiagnosisFormset = inlineformset_factory(Patient, Diagnosisi,
                                         extra=1, form=DiagnosisForm)
