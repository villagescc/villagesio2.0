from __future__ import unicode_literals

from django.db import models

from six import python_2_unicode_compatible

@python_2_unicode_compatible
class Categories(models.Model):
    categories_text = models.CharField(max_length=200)
    icon = models.ImageField(upload_to='categories', blank=True, null=True)

    def __str__(self):
        return "{}".format(self.categories_text)


@python_2_unicode_compatible
class SubCategories(models.Model):
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE)
    sub_categories_text = models.CharField(max_length=220)

    def __str__(self):
        return "{}".format(self.sub_categories_text)
