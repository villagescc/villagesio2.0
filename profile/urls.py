from django.conf.urls import patterns, url
from django.contrib.auth.views import logout

from feed.views import feed
from profile.models import Profile

urlpatterns = patterns(
    'profile.views',
    url(r'^check_invitation/$', 'check_invitation', name='check_invitation'),
    url(r'^register/$', 'register', name='register'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', logout, name='logout', kwargs=dict(next_page='/')),
    url(r'^forgot/$', 'forgot_password', name='forgot_password'),
    url(r'^resetpass/([^/]+)/$', 'reset_password', name='reset_password'),
    url(r'^settings/$', 'edit_settings', name='settings'),
    url(r'^profiles/$', feed,
        dict(item_type=Profile, template='profiles.html', do_filter=True),
        name='profiles'),
    url(r'^profiles/([^/]+)/$', 'profile', name='profile'),
    url(r'^profiles/my_profile', 'my_profile', name='my_profile'),
    url(r'^profiles/([^/]+)/posts/$', 'profile_posts', name='profile_posts'),
    url(r'^contact/', 'undefined_contact', name='undefined_contact'),
    url(r'^profiles/([^/]+)/endorsements/$', 'profile_endorsements',
        name='profile_endorsements'),
    url(r'^profiles/([^/]+)/contact/$', 'contact', name='contact'),
    url(r'^invite/$', 'invite', name='invite'),
    url(r'^invitations/([^/]+)/$', 'invitation', name='invitation'),
    url(r'^invitations/$', 'invitations_sent', name='invitations_sent'),
    url(r'^request_invitation/$', 'request_invitation',
        name='request_invitation'),
    url(r'^share/$', 'share', name='share'),
    url(r'^add_profile_tag/', 'add_profile_tag', name='add_profile_tag'),
    url(r'^delete_profile_tags', 'delete_profile_tags', name='delete_profile_tags'),
)
