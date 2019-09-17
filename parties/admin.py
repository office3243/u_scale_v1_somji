from django.contrib import admin
from .models import Party, Wallet, WalletAdvance

admin.site.register(Party)
admin.site.register(Wallet)
admin.site.register(WalletAdvance)

