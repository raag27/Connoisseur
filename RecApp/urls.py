from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup', views.signup, name='signup'),
    url(r'^recommend',views.recommend,name='recommend'),
    url(r'^feedback',views.rate,name='feedback'),
    ]
