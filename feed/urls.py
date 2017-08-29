from django.conf.urls import patterns, url

urlpatterns = patterns(
    'feed.views',
    url(r'^$', 'feed', {'do_filter': True}, name='feed'),
)
