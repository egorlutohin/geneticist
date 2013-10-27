#coding: utf8
from datetime import datetime, timedelta
from itertools import chain

from dateutil.relativedelta import relativedelta
from django.db.models import Q, F, Count
from django.template import RequestContext
from django.shortcuts import render_to_response

from patient.models import Patient
from user_profile.decorators import login_required

from forms import PeriodForm


MARRIAGEABLE_AGE = relativedelta(years=18)


@login_required
def life(request):
    """ Отчет количества живых пациентов по возрастам за период """
    period_form = PeriodForm(request.GET)
    
    special_cure_text = ''
    header = u'Все'
    
    data = {'period_form': period_form, 'is_have_result': False}
    if len(request.GET) == 0:
        # Если поиск не запускали, то и не надо показывать всех пациентов
        return render_to_response('analytic/life.html', data,
                              context_instance=RequestContext(request))

    
    if period_form.is_valid():
        start = period_form.cleaned_data['period_start']
        end = period_form.cleaned_data['period_end']
        type_residence = period_form.cleaned_data.get('type_residence')
        
        birthday_range = (start, end)
        death_cnd = Q(death__gt=start) | Q(death__isnull=True)
        qs = Patient.objects.filter(death_cnd) \
                            .exclude(type=Patient.FAMILY_MEMBER)
        # ищем в истории место пребывания
        if type_residence:
            if start == end:
                qs = qs.filter(type=type_patient)
            else:
                pks = Patient.history.exclude(type=Patient.FAMILY_MEMBER) \
                                     .filter(type_residence=type_residence,
                                             history_date__lt=end) \
                                     .values('pk') \
                                     .annotate(Count('pk')) \
                                     .values_list('pk')
                pks = tuple(pks)
                qs = qs.filter(pk__in=pks)

        marriageble_birthday = start - MARRIAGEABLE_AGE
        childrens = qs.filter(birthday__gt=marriageble_birthday,
                              birthday__lte=end,
                              type=Patient.FETUS)
        marriageable = qs.filter(birthday__lte=marriageble_birthday,
                                 type=Patient.FETUS)
        fetus_cnd = Q(type=Patient.PROBAND) | Q(birthday__gte=F('date_created'))
        fetus = qs.filter(fetus_cnd)
        data.update({'children': childrens.count(),
                     'marriageable': marriageable.count(),
                     'fetus': fetus.count(),
                     'is_have_result': True})
    else:
        data.update({'children': '-',
                     'marriageable': '-',
                     'fetus': '-'})

#    response = {'patients': patients_qs,
#                'count': patients_qs.count(),
#                'special_cure_text': special_cure_text,
#                'form': form,
#                'header': header,
#                'have_search_result': True}
    return render_to_response('analytic/life.html',
                              data,
                              context_instance=RequestContext(request))
