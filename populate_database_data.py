import os
from django.db import IntegrityError

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"

import django

django.setup()

from categories.models import Categories, SubCategories
from django.contrib.auth.models import User

categories = ['SERVICES', 'PRODUCTS', 'HOUSING', 'RIDESHARE']

product_subcategories = ['OTHER', 'TRAVEL', 'GARDEN', 'FILM & MOVIES', 'PETS & ANIMALS', 'ELECTRONICS',
                         'FOOD & KITCHEN', 'CAMPING & OUTDOORS', 'FURNITURE', 'GAMES & TOYS', 'BOOKS & MAGAZINES',
                         'MUSIC', 'SPORTS', 'TOOLS', 'CLOTHES & ACCESSORIES']

services_subcategories = ["AUTOMOTIVE", "BEAUTY", "COMPUTER", "CYCLE", "FARM+GARDEN", "FINANCIAL", "LABOR",
                          "LEGAL", "PET", "REAL ESTATE", "SKILLED TRADE", "THERAPEUTIC", "MEDIA", "OTHER", "EDUCATION"]

housing_subcategories = ["HOUSING", "FARM", "APARTMENTS", "SHARED", "TEMP", "WORKTRADE", "SWAP"]


for each_c in categories:
    c = Categories(categories_text=each_c)
    c.save()


product_id = Categories.objects.filter(categories_text="PRODUCTS")
services_id = Categories.objects.filter(categories_text="SERVICES")
housing_id = Categories.objects.filter(categories_text="HOUSING")

for prod_sub in product_subcategories:
    s = SubCategories(categories_id=product_id[0].id, sub_categories_text=prod_sub)
    s.save()

for serv_sub in services_subcategories:
    ss = SubCategories(categories_id=services_id[0].id, sub_categories_text=serv_sub)
    ss.save()

for housing_sub in housing_subcategories:
    hs = SubCategories(categories_id=housing_id[0].id, sub_categories_text=housing_sub)
    hs.save()

try:
    User.objects.create_superuser('admin', email='web@villages.cc', password='admin')
except IntegrityError:
    pass