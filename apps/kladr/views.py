#coding: utf8
import json

from django.db.models import Q
from django.http import HttpResponse

from models import Kladr, Doma, Street, Socr
from models import REGION_LEVEL, DISTRICT_LEVEL, CITY_LEVEL, HOUSE_LEVEL
from models import STREET_LEVEL, VILAGE_LEVEL


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


def get_streets(code):
    return Street.objects.filter(code__endswith='00', code__startswith=code)


def get_district_level(code):
    # Области
    districts = get_kladr(DISTRICT_LEVEL, code)
    # Города
    city_startswith = code + '000'
    cities = get_kladr(CITY_LEVEL, city_startswith)
    # Нас. пункты
    vilage_startswith = city_startswith + '000'
    vilages = get_kladr(VILAGE_LEVEL, vilage_startswith)
    # Улицы
    street_startswith = vilage_startswith + '000'
    streets = get_streets(street_startswith)
    info = {}
    #  id_объекта___Уровень
    id_template = '%s___%s'
    if districts.exists():
        info[u'Районы'] = []
        for district in districts:
            district_param = (district.get_district_code(), DISTRICT_LEVEL,)
            district_id = id_template % district_param
            info[u'Районы'].append({'id': district_id,
                                    'value': district.name})
    if cities.exists():
        info[u"Города"] = []
        for city in cities:
            city_param = (city.get_city_code(), CITY_LEVEL,)
            city_id = id_template % city_param
            info[u'Города'].append({'id': city_id,
                                    'value': city.name})
    if vilages.exists():
        info[u"Населенные пункты"] = []
        for vilage in vilages:
            vilage_param = (vilage.get_vilage_code(), VILAGE_LEVEL,)
            vilage_id = id_template % vilage_param
            socr_vilages = get_socr_dict(VILAGE_LEVEL)
            name = u"%s %s" % (vilage.name, socr_vilages[vilage.socr])
            info[u'Населенные пункты'].append({'id': vilage_id,
                                                'value': name})
    if streets.exists():
        info[u"Улицы"] = []
        for street in streets:
            street_param = (street.get_street_code(), STREET_LEVEL,)
            street_id = id_template % street_param
            socr_streets = get_socr_dict(STREET_LEVEL)
            name = u"%s %s" % (street.name, socr_vilages[street.socr])
            info[u'Улицы'].append({'id': street_id,
                                    'value': name})
    return info


def get_city_level(code):
    socr = get_socr_dict(CITY_LEVEL)
    socr.update(get_socr_dict(_LEVEL))
    # Поселения
    vilage_startswith = code + '000'
    vialges = get_kladr(VILAGE_LEVEL, code)
    # Города
    cities = get_kladr(CITY_LEVEL, code)
    info = {u'Районы': [], u'Города': []}
    #  id_объекта___Уровень
    id_template = '%s___%s'
    for city in cities:
        city_param = (city.get_city_code(), CITY_LEVEL,)
        city_id = id_template % city_param
        info[u'Города'].append({'id': city_id,
                                'value': city.name})
    for vilage in vilages:
        vilage_param = (vilage.get_vilage_code(), VILAGE_LEVEL,)
        vilage_id = id_template % vilage_param
        info[u'Районы'].append({'id': vilage_id,
                                'value': vilage.name})
    return info
    


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
    elif level == DISTRICT_LEVEL:
        return HttpResponse(json.dumps(get_district_level(code)))
    else:
        items = get_kladr(level, code)
    for item in items:
        name = u'%s (%s)' % (item.name, socr[item.socr],)
        info.append({'id': getattr(item, LEVEL_CHOICES[level])(),
                      'value': name})
    return HttpResponse(json.dumps(info))
