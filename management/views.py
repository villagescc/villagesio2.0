from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from relate.models import Endorsement
from profile.models import Settings, Profile
from feed.models import FeedItem
from management.forms import FormSearchUsers


def management(request):
    if request.method == 'POST':
        form = FormSearchUsers(request.POST)
        if form.is_valid():
            users = User.objects.filter(username__icontains=form.cleaned_data['search']).all()
            return render(request, 'management_urls.html', {'form': form, 'users': users, 'user_tab': True})
    else:
        users = User.objects.all()
        form = FormSearchUsers()
        return render(request, 'management_urls.html', {'form': form, 'users': users})


def delete_users(request, user_id=''):
    if request.method == 'POST' and request.is_ajax():
        list_users_to_remove = []
        for user_id in request.POST.getlist('ids[]'):
            list_users_to_remove.append(int(user_id))
        users_to_remove = User.objects.filter(id__in=list_users_to_remove)
        try:
            for user in users_to_remove:
                FeedItem.objects.filter(poster_id=user.profile.id).delete()
                FeedItem.objects.filter(recipient_id=user.profile.id).delete()
                Settings.objects.filter(profile_id=user.profile.id).delete()
                Endorsement.objects.filter(endorser_id=user.profile.id).delete()
                Endorsement.objects.filter(recipient_id=user.profile.id).delete()
                Profile.objects.filter(id=user.profile.id).delete()
                User.objects.filter(id=user.id).delete()
        except Exception as e:
            messages.add_message(request, messages.ERROR, 'An error occurred, please try again later')
    return HttpResponseRedirect(reverse('management:management'))


