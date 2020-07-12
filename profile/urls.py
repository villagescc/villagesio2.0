from django.conf.urls import url
from django.contrib.auth.views import LogoutView

from feed.views import feed
from profile.models import Profile
from profile import views

urlpatterns = [
    url(r'^check_invitation/$', views.check_invitation, name='check_invitation'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout', kwargs=dict(next_page='/')),
    url(r'^forgot/$', views.forgot_password, name='forgot_password'),
    url(r'^resetpass/([^/]+)/$', views.reset_password, name='reset_password'),
    url(r'^settings/$', views.edit_settings, name='settings'),
    url(r'^profiles/$', feed,
        dict(item_type=Profile, template='profiles.html', do_filter=True),
        name='profiles'),
    url(r'^profiles/([^/]+)/$', views.profile, name='profile'),
    url(r'^profiles/my_profile', views.my_profile, name='my_profile'),
    url(r'^profiles/([^/]+)/posts/$', views.profile_posts, name='profile_posts'),
    url(r'^contact/', views.undefined_contact, name='undefined_contact'),
    url(r'^profiles/([^/]+)/endorsements/$', views.profile_endorsements,
        name='profile_endorsements'),
    url(r'^profiles/([^/]+)/contact/$', views.contact, name='contact'),
    url(r'^invite/$', views.invite, name='invite'),
    url(r'^invitations/([^/]+)/$', views.invitation, name='invitation'),
    url(r'^invitations/$', views.invitations_sent, name='invitations_sent'),
    url(r'^request_invitation/$', views.request_invitation,
        name='request_invitation'),
    url(r'^share/$', views.share, name='share'),
    url(r'^add_profile_tag/', views.add_profile_tag, name='add_profile_tag'),
    url(r'^delete_profile_tags', views.delete_profile_tags, name='delete_profile_tags'),
]
