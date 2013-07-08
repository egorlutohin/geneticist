#coding: utf8
from django.db import models


class Organization(models.Model):
    """ Названия мед. организаций """
    code = models.CharField(u'Код МО', max_length=7, unique=True)
    short_name = models.CharField(u'Краткое название', max_length=300)
    full_name = models.TextField(verbose_name=u'Полное название')
    name = models.TextField(verbose_name=u'Нормальное название')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Название организации'
        verbose_name_plural = u'Названия организаций'
        ordering = ['name']

    def save(self, *args, **kwargs):
        from patient.models import Patient, Visit

        if self.pk is not None:
            Patient.objects.filter(allocate_mo=self) \
                           .update(code_allocate_mo=self.code,
                                   name_allocate_mo=self.full_name)
            Visit.objects.filter(mo=self) \
                         .update(code=self.code, name=self.full_name)
        super(Organization, self).save(*args, **kwargs)
