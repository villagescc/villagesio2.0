from django.conf.urls import patterns, url

urlpatterns = patterns(
    'admin.views',
    url(r'^email/$', 'email_users', name='email_users'),
)
