from django.contrib import admin
from .models import AccountTransaction, Payment, WalletTransaction, CashTransaction

admin.site.register(Payment)
admin.site.register(AccountTransaction)
admin.site.register(CashTransaction)
admin.site.register(WalletTransaction)

