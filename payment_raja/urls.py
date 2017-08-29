from django.conf.urls import url
# frontend views import
from payment_raja import views


urlpatterns = [
    url(r'^$', views.payment, name='payment_raja'),
]
