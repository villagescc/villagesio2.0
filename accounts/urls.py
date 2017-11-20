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
    url(r'^settings/$', profile_views.edit_settings, name='settings'),
    url(r'^login/$', account_views.login_view, name='login'),
    url(r'^logout/$', account_views.logout_view, name='logout'),
    url(r'^sign_in/', include(accounts.sign_in.urls, namespace='sign_in_user'))
]
