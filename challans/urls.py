from django.conf.urls import url
from . import views

app_name = "challans"

urlpatterns = [
    url(r'^raw_create/$', views.ChallanRawCreateView.as_view(), name="raw_create"),
    url(r'^create/$', views.challan_create, name="create"),
    url(r'^update/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.challan_update, name="update"),
    url(r'^weight_create/$', views.weight_create, name="weight_create"),
    # url(r'^create/$', views.ChallanCreateView.as_view(), name="create"),
]
