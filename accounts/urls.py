from django.conf.urls import url, include

# Import Accounts views
from accounts import views as account_views
from profile import views as profile_views
import accounts.sign_in.urls
from feed.views import feed
from profile.models import Profile

urlpatterns = [
    url(r'^check_invitation/$', profile_views.check_invitation, name='check_invitation'),
    url(r'^account/$', profile_views.profile, name='account'),
    url(r'^forgot/$', profile_views.forgot_password, name='forgot_password'),
    url(r'^resetpass/([^/]+)/$', profile_views.reset_password, name='reset_password'),
    # url(r'^my_profile/$', account_views.my_profile, name='my_profile'),
    # url(r'^profiles/$', feed,
    #     dict(item_type=Profile, template='profiles.html', do_filter=True),
    #     name='profiles'),
    # url(r'^profiles/([^/]+)/posts/$', profile_views.profile_posts, name='profile_posts'),
    # url(r'^profiles/([^/]+)/endorsements/$', profile_views.profile_endorsements,
    #     name='profile_endorsements'),
    # url(r'^profiles/([^/]+)/contact/$', profile_views.contact, name='contact'),
    # url(r'^invite/$', profile_views.invite, name='invite'),
    # url(r'^invitations/([^/]+)/$', profile_views.invitation, name='invitation'),
    # url(r'^invitations/$', profile_views.invitations_sent, name='invitations_sent'),
    # url(r'^request_invitation/$', profile_views.request_invitation,
    #     name='request_invitation'),
    # url(r'^share/$', profile_views.share, name='share'),
    url(r'^settings/$', profile_views.edit_settings, name='settings'),
    url(r'^login/$', account_views.login_view, name='login'),
    url(r'^logout/$', account_views.logout_view, name='logout'),
    url(r'^sign_in/', include(accounts.sign_in.urls, namespace='sign_in_user'))
]
