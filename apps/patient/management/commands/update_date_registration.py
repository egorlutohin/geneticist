#coding: utf8
from django.core.management.base import BaseCommand, CommandError

from common_helpers import nested_commit_on_success
from patient.models import Visit, Patient


class Command(BaseCommand):
    help = u"Поле date_registration в модели Patient такое же как на первом визите"

    @nested_commit_on_success
    def handle(self, *args, **options):
        first_qs = Visit.objects.filter(is_add=True) \
                                .values_list('patient__pk', 'date_created')
        updated = 0
        for pk, date_created in first_qs:
            Patient.objects.filter(pk=pk) \
                           .update(date_registration=date_created)
            updated += 1
        print 'Updated %s records' % updated
