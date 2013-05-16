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
        first_code = second_code = third_code = ''
        first = second = None

        reader = csv.reader(open(settings.MKB_FILE))
        row_number = 0
        for row in reader:
            curr_first_code = row[0]
            if first_code != curr_first_code:
                curr_first_name = row[1]
                first = Mkb.objects.create(code=curr_first_code,
                                           name=curr_first_name)
                first_code = curr_first_code
            full_code = row[4]
            if full_code == third_code:  # в справочнике дублируются записи
                continue
            third_code = full_code
            curr_second_code = full_code.split('.')[0]
            row_number += 1
            if second_code != curr_second_code:
                curr_second_name = row[5]
                second = Mkb.objects.create(code=curr_second_code,
                                            name=curr_second_name,
                                            parent=first)
                second_code = curr_second_code
            else:
                curr_third_name = row[5]
                Mkb.objects.create(code=full_code,
                                   name=curr_third_name,
                                   parent=second)
