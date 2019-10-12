from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r"^", include('portal.urls', namespace="portal")),
    url(r"^accounts/", include('accounts.urls', namespace="accounts")),
    url(r"^challans/", include('challans.urls', namespace="challans")),
    url(r"^payments/", include('payments.urls', namespace="payments")),
    url(r"^parties/", include('parties.urls', namespace="parties")),
    url(r"^materials/", include('materials.urls', namespace="materials")),
    url(r"^rates/", include('rates.urls', namespace="rates")),
    url(r"^bank_accounts/", include('bank_accounts.urls', namespace="bank_accounts")),
]
