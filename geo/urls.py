from django.conf.urls import patterns, url

urlpatterns = patterns(
    'geo.views',
    url(r'^locator/$', 'locator', name='locator'),
)
