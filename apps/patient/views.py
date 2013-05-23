#coding: utf8
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from common_helpers import nested_commit_on_success

from forms import PatientForm, VisitForm, DiagnosisForm, SearchForm
from forms import DiagnosisFormset, VisitFormset
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


def edit(request, patient_id):
    """ Просмотр и изменение информации о пациенте """
    avalible_error = False
    if request.method == "POST":
        instance_patient_id = request.POST.get('id')
        if instance_patient_id:
            instance_patient = get_object_or_404(Patient,
                                                 pk=request.POST['id'])
            diagnosis_qs = instance_patient.diagnosis_set.all()
            visits_qs = instance_patient.visits_set.all()
        else:
            instance_patient = None
            diagnosis_qs = Diagnosis.objects.none()
            visits_qs = Visit.objects.none()
        patient_form = PatientForm(request.POST or None,
                                   instance=instance_patient)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
        else:
            patient = None
            avalible_error = True
        visit_formset = VisitFormset(request.POST or None, instance=patient)
        if not visit_formset.is_valid():
            avalible_error = True
        diagnosis_formset = DiagnosisFormset(request.POST or None,
                                             instance=patient)
        if not diagnosis_formset.is_valid():
            avalible_error = True
        if not avalible_error:
            patient.save()
            diagnosis_formset.save()
            visit_formset.save()

    response = {'patient_forn': patient_form,
                'diagnosis_formset': diagnosis_formset,
                'visit_formset': visit_formset}
    return render_to_response('patient.html',
                              response,
                              context_instance=RequestContext(request))


@nested_commit_on_success
def add(request):
    """ Просмотр и изменение информации о пациенте """
    avalible_error = False
    error_texts = []
    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
        else:
            patient = None
            avalible_error = True
        visit_formset = VisitFormset(request.POST,
                                     prefix=VISIT_PREFIX)
        if not visit_formset.is_valid():
            avalible_error = True
        elif len(visit_formset.forms) < 1:
            avalible_error = True
            error_texts.append(u'Нужно написать куда пришел пациент')
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
            save_formset(visit_formset, patient)
            patient.diagnosis_text = get_diagnosis_text(patient)
            patient.save()
    else:
        patient_form = PatientForm()
        diagnosis_formset = DiagnosisFormset(prefix=DIAGNOSIS_PREFIX)
        visit_formset = VisitFormset(prefix=VISIT_PREFIX)

    response = {'patient_forn': patient_form,
                'diagnosis_formset': diagnosis_formset,
                'visit_formset': visit_formset,
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
