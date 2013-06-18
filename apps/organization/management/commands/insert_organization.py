#coding: utf8
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from common_helpers import nested_commit_on_success
from organization.models import Organization

class Command(BaseCommand):
    help = 'Importing medicial organization csv file'

    @nested_commit_on_success
    def handle(self, *args, **options):
        reader = csv.reader(open(settings.ORGANIZATION_FILE))
        row_number = 0
        for row in reader:
            code = row[0]
            full_name = row[1]
            short_name = row[2]
            name = row[3]
            Organization.objects.create(code=code,
                                        name=name,
                                        full_name=full_name,
                                        short_name=short_name)
