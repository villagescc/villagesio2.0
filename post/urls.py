from django.conf.urls import patterns, url

from feed.views import feed
from post.models import Post

urlpatterns = patterns(
    'post.views',
    url(r'^$', feed, dict(item_type=Post, template='posts.html', do_filter=True),
        name='posts'),
    url(r'^new/$', 'edit_post', name='new_post'),
    url(r'^(\d+)/$', 'view_post', name='view_post'),
    url(r'^(\d+)/edit/$', 'edit_post', name='edit_post'),
)
