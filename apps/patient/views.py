#coding: utf8
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from forms import PatientForm, VisitForm, DiagnosisForm, SearchForm
from models import Patient, DiagnosisFormset, VisitFormset


def data(request):
    """ Просмотр и изменение информации о пациенте """
    avalible_error = False
    instance_patient_id = request.POST.get('id')
    if instance_patient_id:
        instance_patient = get_object_or_404(Patient,
                                             pk=request.POST['id'])
        diagnosis_qs = instance_patient.diagnosis_set.all()
        visits_qs = instance_patient.visits_set.all()
    else:
        instance = None
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
    return render_to_response('templates/patient.html',
                              response,
                              context=RequestContext(request))


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
                              context=RequestContext(request) 
