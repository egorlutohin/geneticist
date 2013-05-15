#coding: utf8
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from common_helpers import nested_commit_on_success
from mkb.models import Mkb

class Command(BaseCommand):
    help = 'Importing MKB-10 csv file'

    @nested_commit_on_success
    def handle(self, *args, **options):
        table = Table(settings.MKB_FILE, codepage='cp866')
        table.open()
        for record in table:
            code = record.ds
            if 
            try:
                mkb = Mkb.objects.get(code=code)
            except Mkb.DoesNotExists:
                mkb = Mkb(code=code, name=record.name)

