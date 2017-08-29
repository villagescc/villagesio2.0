from django.conf.urls import url, include
import pre_transactions.views as pre_transaction_views

urlpatterns = [
    url(r'^trust/$', pre_transaction_views.trust, name='pre_trust'),
    url(r'^pay/$', pre_transaction_views.pay, name='pre_pay')
]