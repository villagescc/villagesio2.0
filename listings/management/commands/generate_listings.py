import uuid
import random
import requests

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from random_words import RandomWords, LoremIpsum

from listings.models import Listings, LISTING_TYPE
from categories.models import SubCategories
from profile.models import Profile


class Command(BaseCommand):
    help = 'Generate random listings and save it to database'

    def add_arguments(self, parser):
        parser.add_argument('quantity', type=int)

    def get_images(self):
        images_links = [
            'https://i.ytimg.com/vi/kug5rJNOGIE/hqdefault.jpg',
            'https://image.freepik.com/free-vector/best-offer-banner_1176-260.jpg',
            'https://hellogaztelu2008.files.wordpress.com/2008/11/many-things.jpg',
            'https://r.btcdn.co/2205/original/305364-BAJA.Son-tantas-cosas_7.jpg',
            'https://i0.wp.com/www.brainpickings.org/wp-content/uploads/2015/03/carsonellis_home.jpg?w=680&ssl=1'
        ]
        images_paths = []
        for image_link in images_links:
            response = requests.get(image_link, timeout=10)
            if response.status_code == 200:
                image = default_storage.save('listings/{}.jpg'.format(uuid.uuid4()), ContentFile(response.content))
                images_paths.append(image)
        return images_paths

    def handle(self, *args, **options):
        quantity = options['quantity']
        listing_types = dict(LISTING_TYPE).values()
        profiles = Profile.objects.all().select_related('user')
        subcategories = SubCategories.objects.all()
        photos = self.get_images()

        rw = RandomWords()
        titles = rw.random_words(count=quantity)
        li = LoremIpsum()
        descriptions = li.get_sentences_list(sentences=quantity)
        listings = []
        for i in range(quantity):
            profile = random.choice(profiles)
            listing_type = random.choice(listing_types)
            listings.append(
                Listings(user=profile.user,
                         profile=profile,
                         title="{} {}".format(listing_type, random.choice(titles)),
                         description=random.choice(descriptions),
                         price=random.randint(1, 45),
                         subcategories=random.choice(subcategories),
                         listing_type=listing_type,
                         photo=random.choice(photos))
            )
        Listings.objects.bulk_create(listings)
