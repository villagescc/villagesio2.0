from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
class Categories(models.Model):
    categories_text = models.CharField(max_length=200)

    def __str__(self):
        return "{}".format(self.categories_text)


@python_2_unicode_compatible
class SubCategories(models.Model):
    categories = models.ForeignKey(Categories)
    sub_categories_text = models.CharField(max_length=220)

    def __str__(self):
        return "{}".format(self.sub_categories_text)
