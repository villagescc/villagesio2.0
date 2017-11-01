import os

os.environ["DJANGO_SETTINGS_MODULE"] = "ccproject.settings"

import django

django.setup()

from django.contrib.auth.models import User

all_users = User.objects.all()

for each_user in all_users:
    try:
        print(each_user.username)
        each_user.username = each_user.username.lower()
        each_user.save()
    except Exception as e:
        pass