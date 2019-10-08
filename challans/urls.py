from django.conf.urls import url
from . import views

app_name = "challans"

urlpatterns = [
    url(r'^add/$', views.ChallanAddView.as_view(), name="add"),
    url(r"^list/$", views.ChallanListView.as_view(), name="list"),
    url(r'^detail/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.ChallanDetailView.as_view(), name="detail"),

    url(r'^entries/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.ChallanEntriesView.as_view(), name="entries"),
    url(r'^entries/done/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.entries_done, name="entries_done"),
    url(r'^assign/reports/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.assign_reports, name="assign_reports"),
    url(r'^assign/rates/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.assign_rates, name="assign_rates"),
    url(r'^done/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.ChallanDoneView.as_view(), name="done"),

    url(r'^weight_entry/create/$', views.weight_entry_create, name="weight_entry_create"),
    url(r'^publish/(?P<challan_no>[0-9a-zA-Z-]+)/$', views.challan_publish, name="publish"),

]
