from django.contrib import admin
from .models import Party, Wallet, WalletAdvance


def get_party_name(instance):
    return instance.party.name


class PartyAdmin(admin.ModelAdmin):

    list_display = ("party_code", "name", "phone", "email", "is_wallet_party")


class WalletAdmin(admin.ModelAdmin):

    list_display = (get_party_name, "balance", "deduct_type", "fixed_amount", "is_active")


admin.site.register(Party, PartyAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(WalletAdvance)

