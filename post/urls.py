from django.conf.urls import url

from feed.views import feed
from post.models import Post
from post import views

urlpatterns = [
    url(r'^$', feed, dict(item_type=Post, template='posts.html', do_filter=True),
        name='posts'),
    url(r'^new/$', views.edit_post, name='new_post'),
    url(r'^(\d+)/$', views.view_post, name='view_post'),
    url(r'^(\d+)/edit/$', views.edit_post, name='edit_post'),
]
