from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.MaterialListView.as_view(), name='list'),
]