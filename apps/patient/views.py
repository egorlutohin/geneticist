#coding: utf8
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from common_helpers import nested_commit_on_success

from forms import PatientForm, VisitForm, DiagnosisForm, SearchForm
from forms import DiagnosisFormset, VisitForm
from models import Patient, Diagnosis, Visit


DIAGNOSIS_PREFIX = 'diagnosis'
VISIT_PREFIX = 'visit'


def save_formset(formset, patient):
    for form in formset.forms:
        item = form.save(commit=False)
        item.patient = patient
        item.save()


def get_diagnosis_text(patient):
    d_txt = []
    template = "%s (%s)"
    for diagnosis in patient.diagnosis_set.all():
        text = template % (diagnosis.name, diagnosis.code)
        d_txt.append(text)
    return "\n".join(d_txt)


@nested_commit_on_success
def edit(request, patient_id): # TODO: нужно доделать + обсудить когда посещение обязательно
    """ Просмотр и изменение информации о пациенте """
    patient = get_object_or_404(Patient, pk=patient_id)
    diagnosis_qs = instance_patient.diagnosis_set.all()
    visits_qs = instance_patient.visits_set.all()
    avalible_error = False
    if request.method == "POST":
        patient_form = PatientForm(request.POST,
                                   instance=instance_patient)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
        visit_form = VisitForm(request.POST, instance=visits_qs)
        if not visit_form.is_valid():
            avalible_error = True
        diagnosis_formset = DiagnosisFormset(request.POST,
                                             instance=diagnosis_qs)
        if not diagnosis_formset.is_valid():
            avalible_error = True
        if not avalible_error:
            patient.save()
            diagnosis_formset.save()
            visit_form.save()
    else:
        patient_form = PatientForm(instance=patient)
        diagnosis_formset = DiagnosisFormset(prefix=DIAGNOSIS_PREFIX,
                                             instance=diagnosis_qs)
        visit_form = VisitForm(prefix=VISIT_PREFIX, instance=visit_form)

    response = {'patient_forn': patient_form,
                'diagnosis_formset': diagnosis_formset,
                'visit_form': visit_form}
    return render_to_response('patient.html',
                              response,
                              context_instance=RequestContext(request))


@nested_commit_on_success
def add(request):
    """ Создание информации о пациенте """
    avalible_error = False
    error_texts = []
    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
        else:
            patient = None
            avalible_error = True
        visit_form = VisitForm(request.POST, prefix=VISIT_PREFIX)
        if not visit_form.is_valid():
            avalible_error = True
        diagnosis_formset = DiagnosisFormset(request.POST,
                                             prefix=DIAGNOSIS_PREFIX)
        if not diagnosis_formset.is_valid():
            avalible_error = True
        elif len(diagnosis_formset.forms) < 1:
            avalible_error = True
            error_texts.append(u'Нужно записать хотя бы 1 диагноз')
        if not avalible_error:
            patient.save()
            save_formset(diagnosis_formset, patient)
            visit = visit_form.save(commit=False)
            visit.patient = patient
            visit.is_add = True
            visit.save()
            patient.diagnosis_text = get_diagnosis_text(patient)
            patient.save()
    else:
        patient_form = PatientForm()
        diagnosis_formset = DiagnosisFormset(prefix=DIAGNOSIS_PREFIX)
        visit_form = VisitForm(prefix=VISIT_PREFIX)

    response = {'patient_forn': patient_form,
                'diagnosis_formset': diagnosis_formset,
                'visit_form': visit_form,
                'error_texts': error_texts}
    return render_to_response('patient.html',
                              response,
                              context_instance=RequestContext(request))



def search(request):
    """ Поиск пациентов """
    patients_qs = Patient.objects.all()
    form = SearchForm(request.GET)
    special_cure_text = ''
    if form.is_valid():
        full_name = form.cleaned_data.get('full_name')
        if full_name:
            patients_qs = patients_qs.filter(full_name__contains=full_name)
        birthday = form.cleaned_data.get('birthday')
        if birthday:
            patients_qs = patients_qs.filter(birthday=birthday)
        special_cure = form.cleaned_data.get('special_cure')
        if special_cure:
            patients_qs = patients_qs.filter(special_cure=special_cure)
            for choice in patient.SPECIAL_CURES:
                if choice[0] == special_cure:
                    special_cure_text = choice[1]
                    break
    response = {'patients': patients_qs,
                'count': patients.count(),
                'special_cure_text': special_cure_text,
                'form': form}
    return render_to_response('templates/search.html',
                              response,
                              context=RequestContext(request))
