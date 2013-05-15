# coding: utf-8

from kladr.models import Kladr, Street, Doma
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


def get_kladr(place, level, id_len1, id_len2, starts_with=''):
    nulles = id_len2 - len(place)
    result = Kladr.objects.filter(
        level=level).extra(select={'id': 'substr(code,1,%s)' % id_len1},
                           where=['substr(code,12,13)=%s',
                                  'substr(code,1,%s)=%s'],
                           params=['00', id_len2, place + '0' * nulles]).values('id', 'name', 'indx', 'socr')
    if starts_with:
        result = result.filter(name__istartswith=starts_with)
    return list(result)


def get_street(place, size=15, starts_with=''):
    nulles = size - len(place)
    result = Street.objects.extra(select={'id': 'substr(code,1,15)'},
                                  where=['substr(code,16,17)=%s',
                                         'substr(code,1,%s)=%s'],
                                  params=['00', size, place + '0' * nulles]).values('id', 'name', 'indx', 'socr')
    if starts_with:
        result = result.filter(name__istartswith=starts_with)
    return list(result)


def get_dom(place, size=19, starts_with=''):
    nulles = size - len(place)
    result = Doma.objects.extra(select={'id': 'substr(code,1,19)'},
                                where=['substr(code,1,%s)=%s'],
                                params=[size, place + '0' * nulles]).values('id', 'name', 'indx')
    if starts_with:
        result = result.filter(name__istartswith=starts_with)
    return list(result)


def get_info(place, index=''):
    info = {}
    results = [
        ('region', get_kladr(place[:2], 1, 2, 2)),
        ('district', get_kladr(place[:5], 2, 5, 5)),
        ('city', get_kladr(place[:8], 3, 8, 8)),
        ('np', get_kladr(place[:11], 4, 11, 11)),
        ('street', get_street(place[:15])),
        ('dom', get_dom(place[:19])),
    ]
    for key, items in results:
        if len(items):
            info[key] = items[0]
            if items[0]['indx']:
                info['indx'] = items[0]['indx']

    return info


def get_children(place, starts_with):
    lenp = len(place)
    if not place:
        # regions

        result = Kladr.objects.filter(
            level=1).extra(select={'id': 'substr(code,1,2)'},
                           where=[
                           'substr(code,12,13)=%s'],
                           params=['00']).values('id', 'name')
        if starts_with:
            result = result.filter(name__istartswith=starts_with)

        def key(reg1):
            cid = int(reg1['id'])
            if cid in (77, 78):
                return 0
            return ord(reg1['name'][0])

        return sorted(result, key=key)

    else:
        result = []
        if lenp == 2:
            result += get_kladr(place, 2, 5, 2, starts_with=starts_with)
        if lenp <= 5:
            result += get_kladr(place, 3, 8, 5, starts_with=starts_with)
        if lenp <= 8:
            result += get_kladr(place, 4, 11, 8, starts_with=starts_with)
        if lenp <= 11:
            result += get_street(place, size=11, starts_with=starts_with)
        if lenp <= 19:
            # size = 15 if lenp < 19 else 19
            result += get_dom(place, size=15, starts_with=starts_with)

    return result


def is_in_range(num, range_):
    ''' returns True if number `num` is inside range_.

    num - integer
    range_ - string. examples: 1-20, Ч(2-10), Н(1-9), Ч, Н
    '''
    # number may contain only 'Ч' or 'Н'. This means the whole range of odd or
    # even.
    ODD = u'Н'
    EVEN = u'Ч'
    assert ODD in range_ or EVEN in range_ or "-" in range_
    if num % 2 == 0:
        is_odd = False
    else:
        is_odd = True

    if is_odd:
        if EVEN in range_:
            # this is even range, so odd number is not in the even range.
            return False
        if range_ == ODD:
            # this is range for all odd numbers
            return True
        else:
            n = range_.replace(ODD, '')
    else:
        # even numbers
        if ODD in range_:
            # this is range for odd numbers
            return False

        if range_ == EVEN:
            # this is range for all even numbers
            return True
        else:
            n = range_.replace(EVEN, '')
    n = n.replace('(', '').replace(')', '')

    n = n.split("-")
    if ODD in range_ or EVEN in range_:
        rng = range(int(n[0]), int(n[1]) + 3, 2)
    else:
        # range without odd or even numbers
        rng = range(int(n[0]), int(n[1]) + 1)

    return num in rng


def get_code_by_place(city, street, house):
    ''' returns post code for address. Raises ObjectDoesNotExist if city or
     street does not exist or MultipleObjectsReturned if there is too much
     streets or cities '''
    city_obj = Kladr.objects.get(name=city)
    street_obj = Street.objects.get(
        name=street, code__startswith=city_obj.get_city_code())

    houses_qs = Doma.objects.filter(
        code__startswith=street_obj.get_street_code())
    post_code = None
    house_int = None  # integer of the house. Need to properly process ranges

    try:
        house_int = int(house)
    except TypeError:
        pass
    except ValueError:
        pass

    # loop over all houses in the kladr houses
    for house_obj in houses_qs:
        # check for exact match
        if house == house_obj.name:
            return house_obj.indx

        if house_int:
            if "-" in house_obj.name or u"Н" in house_obj.name or u"Ч" in house_obj.name:
                in_range = is_in_range(house_int, house_obj.name)
                if in_range:
                    # check post_code. Maybe we found it in previous ranges
                    if post_code:
                        raise MultipleObjectsReturned(
                            "More than one range in kladr for this house")
                    else:
                        post_code = house_obj.indx

    if not post_code:
        post_code = street_obj.indx

    if post_code:
        return post_code
    raise ObjectDoesNotExist
