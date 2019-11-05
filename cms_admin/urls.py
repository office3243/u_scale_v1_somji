from django.conf.urls import url
from . import views

app_name = "cms_admin"

urlpatterns = [
    url(r"^dashboard/$", views.DashboardView.as_view(), name="dashboard"),
    url(r'^payments/list/$', views.PaymentListView.as_view(), name="payment_list"),
]