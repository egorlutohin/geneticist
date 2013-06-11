#coding: utf8
import json

from django.db.models import Q
from django.http import HttpResponse

from models import Kladr, Doma, Street, Socr, code_level
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
                number = number.replace(u'Н(', '')
                number = number.replace(u'Ч(', '')
                number = number.replace(u')', '')
                raw_start, raw_end = number.split('-')
                start_number, end_number = int(raw_start), (int(raw_end) + 1)
                for r_number in range(start_number, end_number, 2):
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
    # Регионы
    curr_level = code_level(code)
    if curr_level < REGION_LEVEL:
        regions = get_kladr(REGION_LEVEL)
    else:
        regions = Kladr.objects.none()
    # Области
    if curr_level == REGION_LEVEL:
        districts = get_kladr(DISTRICT_LEVEL, code)
        district_startswith = code
    elif curr_level < REGION_LEVEL:
        district_startswith = code + '000'
        districts = get_kladr(DISTRICT_LEVEL, district_startswith)
    else:
        districts = Kladr.objects.none()
        district_startswith = code
    # Города
    if curr_level == DISTRICT_LEVEL:
        cities = get_kladr(CITY_LEVEL, code)
        cities_startswith = code
    elif curr_level < DISTRICT_LEVEL:
        cities_startswith = district_startswith + '000'
        cities = get_kladr(CITY_LEVEL, cities_startswith)
    else:
        cities = Kladr.objects.none()
        cities_startswith = code
    # Нас. пункты
    if curr_level == CITY_LEVEL:
        vilages = get_kladr(VILAGE_LEVEL, code)
        vilages_startswith = code
    elif curr_level < CITY_LEVEL:
        vilages_startswith = cities_startswith + '000'
        vilages = get_kladr(VILAGE_LEVEL, vilages_startswith)
    else:
        vilages = Kladr.objects.none()
        vilages_startswith = code
    # Улицы
    if curr_level == VILAGE_LEVEL:
        streets = get_streets(code)
    elif curr_level < VILAGE_LEVEL:
        street_startswith = vilages_startswith + '000'
        streets = get_streets(street_startswith)
    else:
        streets = Street.objects.none()
    # Дома
    if curr_level == STREET_LEVEL:
        pass
        
    info = {}
    if regions.exists():
        info[u'Регионы'] = []
        for region in regions:
            socr_regions = get_socr_dict(REGION_LEVEL)
            name = u'%s %s' % (region.name, socr_regions[region.socr])
            info[u'Регионы'].append({'id': region.get_region_code(),
                                     'value': name})
    if districts.exists():
        info[u'Районы'] = []
        for district in districts:
            info[u'Районы'].append({'id': district.get_district_code(),
                                    'value': district.name})
    if cities.exists():
        info[u"Города"] = []
        for city in cities:
            info[u'Города'].append({'id': city.get_city_code(),
                                    'value': city.name})
    if vilages.exists():
        info[u"Населенные пункты"] = []
        for vilage in vilages:
            socr_vilages = get_socr_dict(VILAGE_LEVEL)
            name = u"%s %s" % (vilage.name, socr_vilages[vilage.socr])
            info[u'Населенные пункты'].append({'id': vilage.get_vilage_code(),
                                                'value': name})
    if streets.exists():
        info[u"Улицы"] = []
        for street in streets:
            socr_streets = get_socr_dict(STREET_LEVEL)
            name = u"%s %s" % (street.name, socr_streets[street.socr])
            info[u'Улицы'].append({'id': street.get_street_code(),
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
    if level == HOUSE_LEVEL:
        return HttpResponse(json.dumps(get_house(code)))
    else:
        return HttpResponse(json.dumps(get_district_level(code)))
