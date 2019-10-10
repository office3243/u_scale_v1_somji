from django.conf.urls import url
from . import views

app_name = "payments"

urlpatterns = [

    url(r"^add/(?P<challan_no>[0-9a-zA-Z-]+)/$", views.add, name="add"),
    url(r"^list/$", views.PaymentListView.as_view(), name="list"),
    url(r"^detail/(?P<id>[0-9]+)/$", views.PaymentDetailView.as_view(), name="detail"),
]
