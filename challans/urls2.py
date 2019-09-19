from django.conf.urls import url
from . import views

app_name = "challans"

urlpatterns = [
    url(r'^raw_create/$', views.ChallanRawCreateView.as_view(), name="raw_create"),
    url(r'^create/$', views.challan_create, name="create"),
    url(r'^update/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.challan_update, name="update"),

    url(r'^preview/update/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.challan_preview_update, name="preview_update"),
    url(r'^weight_entry/create/$', views.weight_entry_create, name="weight_entry_create"),
    url(r'^publish/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.challan_publish, name="publish"),

]
