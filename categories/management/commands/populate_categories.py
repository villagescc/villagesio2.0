from django.db import IntegrityError
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from categories.models import Categories, SubCategories


class Command(BaseCommand):
    help = 'Populate categories and superuser to database'

    def handle(self, *args, **options):
        categories = ['SERVICES', 'PRODUCTS', 'HOUSING', 'RIDESHARE']

        product_subcategories = ['OTHER', 'TRAVEL', 'GARDEN', 'FILM & MOVIES', 'PETS & ANIMALS', 'ELECTRONICS',
                                 'FOOD & KITCHEN', 'CAMPING & OUTDOORS', 'FURNITURE', 'GAMES & TOYS',
                                 'BOOKS & MAGAZINES', 'MUSIC', 'SPORTS', 'TOOLS', 'CLOTHES & ACCESSORIES']

        services_subcategories = ["AUTOMOTIVE", "BEAUTY", "COMPUTER", "CYCLE", "FARM+GARDEN", "FINANCIAL", "LABOR",
                                  "LEGAL", "PET", "REAL ESTATE", "SKILLED TRADE", "THERAPEUTIC", "MEDIA",
                                  "OTHER", "EDUCATION"]

        housing_subcategories = ["HOUSING", "FARM", "APARTMENTS", "SHARED", "TEMP", "WORKTRADE", "SWAP"]

        Categories.objects.bulk_create([Categories(categories_text=category) for category in categories])

        product_id = Categories.objects.filter(categories_text="PRODUCTS").first()
        services_id = Categories.objects.filter(categories_text="SERVICES").first()
        housing_id = Categories.objects.filter(categories_text="HOUSING").first()

        SubCategories.objects.bulk_create([SubCategories(categories_id=product_id.id, sub_categories_text=prod_sub)
                                           for prod_sub in product_subcategories])

        SubCategories.objects.bulk_create([SubCategories(categories_id=services_id.id, sub_categories_text=serv_sub)
                                           for serv_sub in services_subcategories])

        SubCategories.objects.bulk_create([SubCategories(categories_id=housing_id.id, sub_categories_text=housing_sub)
                                           for housing_sub in housing_subcategories])

        try:
            User.objects.create_superuser('admin', email='web@villages.cc', password='admin')
        except IntegrityError:
            pass
