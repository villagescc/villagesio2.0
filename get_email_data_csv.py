import os
import django
import csv

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"

django.setup()

from profile.models import Profile


profiles = Profile.objects.all()
writer = csv.writer(open("profiles.csv", "ab"), delimiter=',', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['name, email, city, state, neighborhood'])
for each_profile in profiles:
    try:
        profile_data = [each_profile.name,
                        each_profile.email,
                        each_profile.location.city,
                        each_profile.location.state,
                        each_profile.location.neighborhood]
        writer.writerow(profile_data)
        profile_data = [each_profile.name, each_profile.email]
    except Exception as e:
        print(e)