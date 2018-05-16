from django.conf.urls import url
from accounts.sign_in.views import SignInUserPreRegister, SignInUserRegister, SignInUserLogIn, edit_profile

urlpatterns = [
    url(r'^register/$', SignInUserPreRegister.as_view(), name='sign_in_register'),
    url(r'^register/complete/$', SignInUserRegister.as_view(), name='sign_in_complete_register'),
    url(r'^log_in/$', SignInUserLogIn.as_view(), name='sign_in_log_in'),
    url(r'^edit/$', edit_profile, name='edit_profile'),
]