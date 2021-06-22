# coding: utf-8
from __future__ import unicode_literals

from django.urls import include, path

from . import views

app_name = 'robokassa'

urlpatterns = [
    path('result/', views.receive_result, name='result'),
    path('success/', views.success, name='success'),
    path('fail/', views.fail, name='fail'),
]
