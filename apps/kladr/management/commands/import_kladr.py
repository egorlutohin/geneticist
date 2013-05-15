# coding: utf-8
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection as conn
from django.db import transaction as trs

import dbf_rw


DBF_DIR = settings.KLADR_ROOT


def imp_socr(f):
    rd = dbf_rw.dbfreader(open(f, 'rb'))
    print 'file:', f

    fields, type = rd.next(), rd.next()
    print 'fields:', map(lambda x, y: str(x) + str(y), fields, type)

    curs = conn.cursor()  # @UndefinedVariable
    curs.execute('delete from kladr_socr')

    line = 0
    for dbf_row in rd:
        line += 1

        r = [unicode(r, 'cp866').strip() for r in dbf_row]
        curs.execute(
            "insert into kladr_socr(socr,name,level,tcode) values (%s,%s,%s,%s)",
            (r[1], r[2], r[0], r[3],)
        )
        trs.commit_unless_managed()
    print "lines:", line
    rd.close()


def calc_level(code):
    '''mask: SSRRRGGGPPP'''
    if code[8:11] != '000': return 4
    if code[5:8] != '000': return 3
    if code[2:5] != '000': return 2
    return 1


def imp_kladr(f):
    rd = dbf_rw.dbfreader(open(f, 'rb'))
    print 'file:', f

    fields, type = rd.next(), rd.next()
    print 'fields:', map(lambda x, y: str(x) + str(y), fields, type)

    curs = conn.cursor()  # @UndefinedVariable
    curs.execute('delete from kladr_kladr')

    line = 0
    for dbf_row in rd:
        line += 1

        r = [unicode(r, 'cp866').strip() for r in dbf_row]

        curs.execute(
            "insert into kladr_kladr(code,level,name,socr,stat,indx)" +
            " values (%s,%s,%s,%s,%s,%s)",
            (r[2], calc_level(r[2]), r[0], r[1], r[7], r[3])
        )
        trs.commit_unless_managed()
    print "lines:", line
    rd.close()


def imp_street(f):
    rd = dbf_rw.dbfreader(open(f, 'rb'))
    print 'file:', f

    fields, type = rd.next(), rd.next()
    print 'fields:', map(lambda x, y: str(x) + str(y), fields, type)

    curs = conn.cursor()  # @UndefinedVariable
    curs.execute('delete from kladr_street')

    line = 0
    for dbf_row in rd:
        line += 1

        r = [unicode(r, 'cp866').strip() for r in dbf_row]

        curs.execute(
            "insert into kladr_street(code,name,socr,indx)" +
            " values (%s,%s,%s,%s)", (r[2], r[0], r[1], r[3])
        )
        trs.commit_unless_managed()
    print "lines:", line
    rd.close()


def imp_doma(f):
    rd = dbf_rw.dbfreader(open(f, 'rb'))
    print 'file:', f

    fields, type = rd.next(), rd.next()
    print 'fields:', map(lambda x, y: str(x) + str(y), fields, type)

    curs = conn.cursor()  # @UndefinedVariable
    curs.execute('delete from kladr_doma')

    line = 0
    for dbf_row in rd:
        line += 1

        r = [unicode(r, 'cp866').strip() for r in dbf_row]

        curs.execute(
            "insert into kladr_doma(code,name,korp,indx)" +
            " values (%s,%s,%s,%s)", (r[3], r[0], r[1], r[4])
        )
        trs.commit_unless_managed()
    print "lines:", line
    rd.close()


class Command(BaseCommand):
    help = 'Importing kladr dbf files'

    def handle(self, *args, **options):
        imp_socr(os.path.join(DBF_DIR, 'SOCRBASE.DBF'))
        imp_kladr(os.path.join(DBF_DIR, 'KLADR.DBF'))
        imp_street(os.path.join(DBF_DIR, 'STREET.DBF'))
        imp_doma(os.path.join(DBF_DIR, 'DOMA.DBF'))
