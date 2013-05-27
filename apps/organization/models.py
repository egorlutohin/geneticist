#coding: utf8
from django.db import models


class Organization(models.Model):
    """ Названия мед. организаций """
    code = models.CharField(u'Код МКБ', max_length=7, unique=True)
    name = models.CharField(u'Название', max_length=50)
    full_name = models.TextField(verbose_name=u'Полное название')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code,)

    class Meta:
        verbose_name = u'Название организации'
        verbose_name_plural = u'Названия организаций'
