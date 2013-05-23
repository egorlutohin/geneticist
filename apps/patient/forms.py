#coding: utf8
from django import forms
from django.forms.models import inlineformset_factory, formset_factory

from models import Patient, Visit, Diagnosis


class SearchForm(forms.Form):
    """ Форма поиска пациентов """
    full_name = forms.CharField(max_length=300, required=False)
    special_cure = forms.ChoiceField(choices=Patient.SPECIAL_CURES,
                                     required=False)
    birthday = forms.DateField(required=False)


class PatientForm(forms.ModelForm):
    # если одно поле заполенно, то нужно проверять заполнены ли другие поля
    double_required = (('allocate_lpu', 'code_allocate_lpu',),)
    def clear(self):
        cd = self.cleaned_data
        for params in self.double_required:
            avalible = None
            for name in params:
                curr_avalible = bool(cd.get(name))
                if avalible is None:
                    avalible = curr_avalible
                if curr_avalible != avalible:
                    label = self.fields[name].label
                    text = u'%s обязательно для заполнения' % label
                    raise forms.ValidationError(text)
        return cd

    class Meta:
        model = Patient
        exclude = ('is_active',)


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        exclude = ('is_active', 'patient',)


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        exclude = ('is_active', 'patient',)


VisitFormset = formset_factory(VisitForm, extra=1)


DiagnosisFormset = formset_factory(DiagnosisForm,
                                         extra=1)
