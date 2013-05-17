#coding: utf8
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


class Mkb(MPTTModel):
    parent = TreeForeignKey('self',
                            null=True,
                            blank=True,
                            related_name='children')
    code = models.CharField(u'Код МКБ', max_length=7, unique=True)
    name = models.TextField(verbose_name=u'Название')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code,)

    class Meta:
        verbose_name = u'элемент МКБ-10'
        verbose_name_plural = u'Справочник МКБ-10'
