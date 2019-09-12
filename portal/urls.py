from . import views
from django.conf.urls import url

app_name = "portal"

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),

]
