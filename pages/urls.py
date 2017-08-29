from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView

urlpatterns = patterns(
    'pages.views',
    url(r'^$', 'intro', name='home'),
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^about/$', RedirectView.as_view(url='/about/motivation/', permanent=True), name='about'),
    url(r'^about/how/$', TemplateView.as_view(template_name='../about/templates/how_it_works.html'), name='how_it_works_old'),
    url(r'^about/privacy/$', TemplateView.as_view(template_name='../about/templates/privacy.html'), name='privacy'),
    url(r'^about/motivation/$', TemplateView.as_view(template_name='../about/templates/motivation.html'), name='motivation'),
    url(r'^about/developers/$', TemplateView.as_view(template_name='../about/templates/developers.html'), name='developers'),
    url(r'^about/donate/$', TemplateView.as_view(template_name='../about/templates/donate.html'), name='donate'),
)
