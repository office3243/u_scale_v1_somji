from django.contrib import admin
from .models import AccountTransaction, Payment, WalletTransaction


admin.site.register(AccountTransaction)
admin.site.register(Payment)
admin.site.register(WalletTransaction)

