from django.contrib import admin
from .models import Party, Wallet, WalletAdvance


class PartyAdmin(admin.ModelAdmin):

    list_display = ("party_code", "name", "phone", "email", "is_wallet_party")


admin.site.register(Party, PartyAdmin)
admin.site.register(Wallet)
admin.site.register(WalletAdvance)

