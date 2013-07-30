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
            ldap_name = row[1]
            full_name = row[2]
            short_name = row[3]
            name = row[4]
            Organization.objects.create(code=code,
                                        name=name,
                                        full_name=full_name,
                                        short_name=short_name,
                                        ldap_name=ldap_name)
