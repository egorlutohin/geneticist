#coding: utf8
import json

from django.http import HttpResponse

from models import Kladr, Doma, Street, Socr
from models import REGION_LEVEL, DISTRICT_LEVEL, CITY_LEVEL, HOUSE_LEVEL
from models import STREET_LEVEL


LEVEL_CHOICES = {REGION_LEVEL: 'get_region_code',
                 DISTRICT_LEVEL: 'get_district_code',
                 CITY_LEVEL: 'get_city_code',
                 HOUSE_LEVEL: 'get_house_code',
                 STREET_LEVEL: 'get_street_code'}


def get_socr_dict(level):
    return dict([(v.socr, v.name) for v in Socr.objects.filter(level=level)])


def get_house(code):
    qs = Doma.objects.filter(code__startswith=code)
    numbers = {}
    for item in qs:
        for number in item.name.split(','):
            if u'Ч(' == number[:2] or u'Н(' == number[:2]:
                number = number.replace(u'Ч(', '')
                number = number.replace(u'Н(', '')
                number = number.replace(u')', '')
                raw_start, raw_end = number.split('-')
                start_number, end_number = int(raw_start), (int(raw_end) + 1)
                for r_number in range(start_number, end_number):
                    numbers[r_number] = item.indx
            else:
                numbers[number] = item.indx
    return numbers


def get_kladr(level, code_startswith=""):
    qs = Kladr.objects.filter(code__endswith="00", level=level)
    len_code_startswith = len(code_startswith)
    if len_code_startswith:
        qs = qs.filter(code__startswith=code_startswith)
    return qs


def kladr(request):
    """ Выбирает регионы, районы, города, улицы """
    info = []
    level = int(request.GET.get('level', REGION_LEVEL))
    socr = get_socr_dict(level)
    code = request.GET.get('code', '')
    if level == STREET_LEVEL:
        items = Street.objects.filter(code__endswith='00', code__startswith=code)       
    elif level == HOUSE_LEVEL:
        return HttpResponse(json.dumps(get_house(code)))
    else:
        items = get_kladr(level, code)
    for item in items:
        name = u'%s (%s)' % (item.name, socr[item.socr],)
        info.append({'id': getattr(item, LEVEL_CHOICES[level])(),
                      'value': name})
    return HttpResponse(json.dumps(info))
