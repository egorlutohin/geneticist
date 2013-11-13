#coding: utf8
from datetime import datetime, timedelta, date
from itertools import chain

from dateutil.relativedelta import relativedelta
from django.db.models import Q, F, Count
from django.template import RequestContext
from django.shortcuts import render_to_response

from patient.models import Patient, Diagnosis, Visit
from user_profile.decorators import login_required

from forms import PeriodForm


MARRIAGEABLE_AGE = relativedelta(years=18)


@login_required
def main(request):
    """ выводим список всех отчетов """
    return render_to_response('analytic/main.html',
                              context_instance=RequestContext(request))


def get_type_residence_qs(type_residence, date_start, date_end):
    """ Возвращает список id пациентов, у которые жили в type_residence """
    type_residence = int(type_residence)
    ids_hst = Patient.history.exclude(type=Patient.FAMILY_MEMBER) \
                             .filter(history_date__lte=date_end,
                                     type_residence=type_residence) \
                             .values('id')
    history_qs = Patient.history.filter(id__in=ids_hst) \
                                .order_by('id', '-history_date') \
                                .values_list('id',
                                             'type_residence',
                                             'history_date')
    pks = []
    exclude_pks = []
    for pk, type_r, history_date in history_qs:
        if pk in pks or pk in exclude_pks:
            continue
        if type_r == type_residence:
            pks.append(pk)
            continue
        if history_date.date() < date_start:
            exclude_pks.append(pk)
    return pks


@login_required
def life(request):
    """ Отчет количества живых пациентов по возрастам за период """
    period_form = PeriodForm(request.GET)
    
    data = {'period_form': period_form, 'is_have_result': False}
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        data['period_form'] = PeriodForm
        return render_to_response('analytic/life.html', data,
                              context_instance=RequestContext(request))

    
    if period_form.is_valid():
        start = period_form.cleaned_data['period_start']
        end = period_form.cleaned_data['period_end']
        type_residence = period_form.cleaned_data.get('type_residence')
        
        death_cnd = Q(death__gt=start) | Q(death__isnull=True)
        qs = Patient.objects.filter(death_cnd) \
                            .exclude(type=Patient.FAMILY_MEMBER)
        # ищем в истории место пребывания
        if type_residence:
            if start == date.today():
                qs = qs.filter(type_residence=type_residence)
            else:
                pks = get_type_residence_qs(type_residence, start, end)
                qs = qs.filter(pk__in=pks)
                res_info = dict(Patient.TYPE_RESIDENCES)
                data['type_residence'] = res_info.get(int(type_residence), '')

        marriageble_birthday = start - MARRIAGEABLE_AGE
        childrens = qs.filter(birthday__gt=marriageble_birthday,
                              birthday__lte=end,
                              type=Patient.PROBAND)
        marriageable = qs.filter(Q(birthday__lte=marriageble_birthday),
                                 type=Patient.PROBAND,
                                 birthday__lte=end)
        fetus_cnd = Q(type=Patient.FETUS) | \
                    (Q(birthday__gt=F('date_registration')) & Q(birthday__gt=end))
        reg_date = end + timedelta(days=1)
        fetus = qs.filter(fetus_cnd, date_registration__lte=reg_date)
        data.update({'children': childrens.count(),
                     'marriageable': marriageable.count(),
                     'fetus': fetus.count(),
                     'is_have_result': True,
                     'period_start': start,
                     'period_end': end})
    else:
        data.update({'children': '-',
                     'marriageable': '-',
                     'fetus': '-'})

    return render_to_response('analytic/life.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
def nosology(request):
    """ Отчет по нозологиям за период """
    period_form = PeriodForm(request.GET)
    
    data = {'period_form': period_form, 'is_have_result': False}
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        data['period_form'] = PeriodForm
        return render_to_response('analytic/nosology.html', data,
                              context_instance=RequestContext(request))

    
    if period_form.is_valid():
        start = period_form.cleaned_data['period_start']
        end = period_form.cleaned_data['period_end']
        type_residence = period_form.cleaned_data.get('type_residence')
        
        date_range = (start, end + timedelta(days=1))
        death_cnd = Q(death__gt=start) | Q(death__isnull=True)
        patient_qs = Patient.objects.filter(death_cnd,
                                            type=Patient.PROBAND,
                                            birthday__lt=date_range[1])
        # ищем в истории место пребывания
        if type_residence:
            if start == date.today():
                patient_qs = qs.filter(type_residence=type_residence)
            else:
                pks = get_type_residence_qs(type_residence, start, end)
                patient_qs = patient_qs.filter(pk__in=pks)
                res_info = dict(Patient.TYPE_RESIDENCES)
                data['type_residence'] = res_info.get(int(type_residence), '')

        diagnosis_qs = Diagnosis.objects.filter(patient__in=patient_qs) \
                                        .select_related('patient')
        marriageble_birthday = start - MARRIAGEABLE_AGE
        info = {}
        for diagnosis in diagnosis_qs:
            code = diagnosis.code
            if code not in info:
                # название, код, кол-во детей, кол-во взрослых
                info[code] = [diagnosis.name, diagnosis.code, 0, 0]
            if diagnosis.patient.birthday < marriageble_birthday:
                info[code][2] += 1
            else:
                info[code][3] += 1
        info = info.values()
        info.sort(lambda x, y: cmp(x[0], y[0]))
        
        data.update({'info': info,
                     'is_have_result': True,
                     'period_start': start,
                     'period_end': end})
    else:
        data.update({'children': '-',
                     'marriageable': '-',
                     'fetus': '-'})

    return render_to_response('analytic/nosology.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
def new_diagnosis(request):
    """ Отчет по количеству пациентов поставленных диагнозов МО за период """
    period_form = PeriodForm(request.GET)
    
    data = {'period_form': period_form, 'is_have_result': False}
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        data['period_form'] = PeriodForm
        return render_to_response('analytic/new_diagnosis.html', data,
                              context_instance=RequestContext(request))

    
    if period_form.is_valid():
        start = period_form.cleaned_data['period_start']
        end = period_form.cleaned_data['period_end']
        date_range = (start, end + timedelta(days=1))
        qs = Diagnosis.objects.filter(date_created__range=date_range) \
                              .values('user_changed__mo_name') \
                              .annotate(count=Count('pk')) \
                              .order_by('user_changed__mo_name')
        data.update({'info': qs,
                     'is_have_result': True,
                     'period_start': start,
                     'period_end': end})
    else:
        data.update({'info': []})

    return render_to_response('analytic/new_diagnosis.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
def visit(request):
    """ Отчет по количеству посещений МО за период """
    period_form = PeriodForm(request.GET)
    
    data = {'period_form': period_form, 'is_have_result': False}
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        data['period_form'] = PeriodForm()
        return render_to_response('analytic/visit.html', data,
                              context_instance=RequestContext(request))

    
    if period_form.is_valid():
        start = period_form.cleaned_data['period_start']
        end = period_form.cleaned_data['period_end']
        date_range = (start, end + timedelta(days=1))
        qs = Visit.objects.filter(date_created__range=date_range) \
                          .values('name') \
                          .annotate(count=Count('pk')) \
                          .order_by('name')
        data.update({'info': qs,
                     'is_have_result': True,
                     'period_start': start,
                     'period_end': end})
    else:
        data.update({'info': []})

    return render_to_response('analytic/visit.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
def mkb(request):
    """ Отчет заболеваний МКБ за период """
    period_form = PeriodForm(request.GET)
    
    data = {'period_form': period_form, 'is_have_result': False}
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        data['period_form'] = PeriodForm()
        return render_to_response('analytic/mkb.html', data,
                              context_instance=RequestContext(request))

    
    if period_form.is_valid():
        start = period_form.cleaned_data['period_start']
        end = period_form.cleaned_data['period_end']
        date_range = (start, end + timedelta(days=1))
        qs = Diagnosis.objects.filter(date_created__range=date_range) \
                              .values('patient__full_name', 'code', 'name') \
                              .order_by('patient__full_name')
        data.update({'info': qs,
                     'is_have_result': True})
    else:
        data.update({'info': []})

    return render_to_response('analytic/mkb.html',
                              data,
                              context_instance=RequestContext(request))
