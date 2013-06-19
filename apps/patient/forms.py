#coding: utf8
from django import forms
from django.forms.models import formset_factory, modelformset_factory
from django.forms.widgets import HiddenInput

from organization.models import Organization

from models import Patient, Visit, Diagnosis
from widgets import CalendarWidget


class SearchForm(forms.Form):
    """ Форма поиска пациентов """
    _LPU_QS = Visit.objects.filter(is_add=True).values_list('lpu')
    _LPU_ADDED_QS = Organization.objects.filter(pk__in=_LPU_QS)
    full_name = forms.CharField(required=False, label=u'ФИО')
    birthday = forms.DateField(required=False,label=u'Дата рождения',
                               widget=CalendarWidget())
    death = forms.DateField(required=False, label=u'Дата смерти',
                            widget=CalendarWidget())
    diagnosis = forms.CharField(required=False, label=u'Диагноз по МКБ')
    lpu_added = forms.ModelChoiceField(required=False,
                                       label=u'МО внесения в регистр',
                                       queryset=_LPU_ADDED_QS)
    TYPE_RESIDENCES = (('', '-----',),) + Patient.TYPE_RESIDENCES
    type_residence = forms.ChoiceField(required=False,
                                       label=u'Пациент',
                                       choices=TYPE_RESIDENCES)
    SPECIAL_CURES = (('', '-----',),) + Patient.SPECIAL_CURES
    special_cure = forms.ChoiceField(required=False,
                                     label=u'Спец. лечение',
                                     choices=SPECIAL_CURES)
    SOCIAL_STATUSES = (('', '------',),) + Patient.SOCIAL_STATUSES
    social_status = forms.ChoiceField(label=u'Социальный статус',
                                      required=False,
                                      choices=SOCIAL_STATUSES)


class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.iteritems():
            if isinstance(field, forms.DateField):
                self.fields[name].widget = CalendarWidget()

    def clean(self):
        cd = self.cleaned_data
        if not (bool(cd.get('registration')) or bool(cd.get('residence'))):
            text = u'Нужно указать или адрес регистрации или адрес поживания'
            raise forms.ValidationError(text)
        policy_params = ('seria_policy',
                         'number_policy',
                         'code_insurance_company',)

        is_policy_required = None
        for name in policy_params:
            avalible = bool(cd.get(name))
            if is_policy_required is None:
                is_policy_required = avalible
            if is_policy_required != avalible:
                text = u'Нужно полностью заполнить информацию о полисе'
                raise forms.ValidationError(text)
        return cd

    class Meta:
        model = Patient
        exclude = ('is_active', 'user_changed', 'date_changed',
                   'diagnosis_text', 'diagnosis_text_code',
                   'code_allocate_lpu', 'name_allocate_lpu',
                   'full_name', 'prev_full_name', 'all_full_names',)


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        exclude = ('is_active', 'patient', 'user_created', 'date_created',
                   'name', 'code', 'is_add',)


class DiagnosisForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DiagnosisForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget = HiddenInput()
        self.fields['name'].widget = HiddenInput()

    class Meta:
        model = Diagnosis
        exclude = ('is_active', 'patient', 'user_changed', 'date_changed',)


DiagnosisFormset = formset_factory(DiagnosisForm, extra=1, max_num=100)


DiagnosisModelFormset = modelformset_factory(Diagnosis,
                                             form=DiagnosisForm,
                                             extra=1,
                                             max_num=100,
                                             can_delete=True)
