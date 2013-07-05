#coding: utf8
from datetime import datetime, timedelta
from itertools import chain

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect

from common_helpers import nested_commit_on_success

from forms import PatientForm, VisitForm, DiagnosisForm, SearchForm
from forms import DiagnosisFormset, DiagnosisModelFormset
from models import Patient, Diagnosis, Visit


DIAGNOSIS_PREFIX = 'diagnosis'
VISIT_PREFIX = 'visit'
VISIT_FIRST_PREFIX = 'visit-first'
NIGHT_TIME = timedelta(hours=12)
TIME_HISTORY_IGNORE = timedelta(seconds=3)


def save_formset(formset, patient):
    for form in formset.forms:
        if len(form.cleaned_data) == 0:
            continue
        elif form.cleaned_data.get('DELETE', False) and \
             isinstance(form.cleaned_data.get('id'), Diagnosis):
                item = form.cleaned_data.get('id')
                item.delete()
        else:
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


def get_diagnosis_code(patient):
    return "\n".join(patient.diagnosis_set.values_list('code', flat=True))


def clear_ids(request):
    return dict([(k, v) for k, v in request.POST.iteritems() \
                        if (len(v) > 0 and v != u"\r\n")])


@login_required
@nested_commit_on_success
def edit(request, patient_id): # TODO: нужно доделать + обсудить когда посещение обязательно
    """ Просмотр и изменение информации о пациенте """
    patient = get_object_or_404(Patient, pk=patient_id)
    diagnosis_qs = patient.diagnosis_set.all()
    avalible_error = False
    period_visit = datetime.now() - patient.visit_set.latest().date_created
    is_need_save_visit = period_visit > timedelta(hours=12)
    if request.method == "POST":
        patient_form = PatientForm(request.POST,
                                   instance=patient)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
        else:
            avalible_error = True
        visit_form = VisitForm(request.POST, prefix=VISIT_PREFIX)
        if not visit_form.is_valid():
            if period_visit > NIGHT_TIME:
                avalible_error = True
            else:
                is_need_save_visit = False
                visit_form = VisitForm(prefix=VISIT_PREFIX)
        else:
            is_need_save_visit = True

        diagnosis_formset = DiagnosisModelFormset(clear_ids(request),
                                                  prefix=DIAGNOSIS_PREFIX,
                                                  queryset=diagnosis_qs)
        if not diagnosis_formset.is_valid():
            avalible_error = True
        if not avalible_error:
            save_formset(diagnosis_formset, patient)
            patient.diagnosis_text = get_diagnosis_text(patient)
            patient.diagnosis_text_code = get_diagnosis_code(patient)
            patient.save()
            messages.add_message(request,
                                 messages.INFO,
                                 u'Информация о пациенте изменена')
            if is_need_save_visit:
                visit = visit_form.save(commit=False)
                visit.patient = patient
                visit.save()
                visit_form = VisitForm(prefix=VISIT_PREFIX)
            # если все сохранилось, то правильно выводим где флажки "удалить", а где текст
            diagnosis_formset = DiagnosisModelFormset(
                prefix=DIAGNOSIS_PREFIX,
                queryset=patient.diagnosis_set.all()
            )

    else:
        patient_form = PatientForm(instance=patient)
        diagnosis_formset = DiagnosisModelFormset(prefix=DIAGNOSIS_PREFIX,
                                                  queryset=diagnosis_qs)
        visit_form = VisitForm(prefix=VISIT_PREFIX)

    response = {'patient_form': patient_form,
                'diagnosis_formset': diagnosis_formset,
                'visit_form': visit_form,
                'visits_qs': patient.visit_set.all(),
                'patient': patient}
    return render_to_response('patient_edit.html',
                              response,
                              context_instance=RequestContext(request))


@login_required
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
            Patient.objects.filter(pk=patient.pk) \
                           .update(diagnosis_text = get_diagnosis_text(patient),
                                   diagnosis_text_code = get_diagnosis_code(patient))
            messages.add_message(request, messages.INFO, u'Пациент внесен в регистр')
            url = reverse('patient_edit', kwargs={'patient_id': patient.pk})
            return redirect(url)
    else:
        patient_form = PatientForm()
        diagnosis_formset = DiagnosisFormset(prefix=DIAGNOSIS_PREFIX)
        visit_form = VisitForm(prefix=VISIT_PREFIX)

    response = {'patient_form': patient_form,
                'diagnosis_formset': diagnosis_formset,
                'visit_form': visit_form,
                'error_texts': error_texts}
    return render_to_response('patient_add.html',
                              response,
                              context_instance=RequestContext(request))


HEADER_SEARCH = {
    unicode(Patient.NEED_CURE): u'Нуждающиеся в спец. лечении',
    unicode(Patient.NOT_NEED_CURE): u'Не нуждающиеся в спец. лечении',
    unicode(Patient.GET_CURE): u'Получающие спец. лечение',
    unicode(Patient.RAISE_CURE): u'Снятые со спец. лечения'}


@login_required
def search(request):
    """ Поиск пациентов """
    patients_qs = Patient.objects.all()
    form = SearchForm(request.GET)
    special_cure_text = ''
    header = u'Все'
    
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        return render_to_response('search.html',
                              {'form': form, 'have_search_result': False},
                              context_instance=RequestContext(request))

    
    if form.is_valid():
        full_name = form.cleaned_data.get('full_name')
        if full_name:
            patients_qs = patients_qs.filter(all_full_names__icontains=full_name)
        type_residence = form.cleaned_data.get('type_residence')
        if type_residence:
            patients_qs = patients_qs.filter(type_residence=type_residence)
        social_status = form.cleaned_data.get('social_status')
        if social_status:
            patients_qs = patients_qs.filter(social_status=social_status)
        birthday = form.cleaned_data.get('birthday')
        if birthday:
            patients_qs = patients_qs.filter(birthday=birthday)
        death = form.cleaned_data.get('death')
        if death:
            patients_qs = patients_qs.filter(death=death)
        lpu_added = form.cleaned_data.get('lpu_added')
        if lpu_added:
            patients_qs = patients_qs.filter(visit__is_add=True,
                                             visit__lpu=lpu_added)
        special_cure = form.cleaned_data.get('special_cure')
        if special_cure:
            if special_cure in HEADER_SEARCH:
                header = HEADER_SEARCH[special_cure]
            patients_qs = patients_qs.filter(special_cure=special_cure)
        diagnosis = form.cleaned_data.get('diagnosis')
        if diagnosis:
            q_st = Q(diagnosis__code__contains=diagnosis) | \
                   Q(diagnosis__name__contains=diagnosis)
            with_diagnosis = patients_qs.filter(diagnosis__code__contains=diagnosis)
            patients_qs = patients_qs.filter(pk__in=with_diagnosis)
    response = {'patients': patients_qs,
                'count': patients_qs.count(),
                'special_cure_text': special_cure_text,
                'form': form,
                'header': header,
                'have_search_result': True}
    return render_to_response('search.html',
                              response,
                              context_instance=RequestContext(request))


def update_history(history, h_date, username):
    history.append(((h_date, h_date + TIME_HISTORY_IGNORE), username))
    return history


@login_required
def history(request, patient_id):
    """ Список кто изменял в информацию о пациенте """
    patient = get_object_or_404(Patient, pk=patient_id)
    histories_qs = patient.history.filter(history_type='~') \
                                  .values_list('history_date',
                                               'history_user__username')
    histories = [((d, d + TIME_HISTORY_IGNORE), u) for d, u in histories_qs]
    
    visits = patient.visit_set.all()
    diagnosis = patient.diagnosis_set.all()
    for element in chain(visits, diagnosis):
        element_h_qs = element.history.values_list('history_date',
                                                  'history_user__username')
        for element_date, username in element_h_qs:
            is_double_hist = False # Для каждого диагноза и визита пишется своя история.
            for p_date, p_user in histories:
                if p_date[0] <= element_date <= p_date[1] and \
                   p_user == username:
                    is_double_hist = True
            if not is_double_hist:
                histories = update_history(histories,
                                           element_date,
                                           username)

    histories.sort(lambda x, y: cmp(x[0][0], y[0][0]))
    response = {'histories': histories,
                'patient': patient}
    return render_to_response('patient_history.html',
                              response,
                              context_instance=RequestContext(request))
