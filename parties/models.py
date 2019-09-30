from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class PartyCategory(models.Model):

    name = models.CharField(max_length=64)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Party(models.Model):

    party_category = models.ForeignKey(PartyCategory, blank=True, null=True, on_delete=models.SET_NULL)
    rate_group = models.ForeignKey("rates.RateGroup", on_delete=models.PROTECT)

    name = models.CharField(max_length=128)
    code = models.CharField(max_length=32)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=13)
    whatsapp = models.CharField(max_length=13)
    email = models.EmailField(blank=True, null=True)

    is_wallet_party = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

    @property
    def get_wallet(self):
        try:
            return Wallet.objects.get(party=self, is_active=True)
        except:
            return None

    @property
    def get_bank_accounts(self):
        return self.bankaccount_set.filter(is_active=True)

    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"


class Wallet(models.Model):

    DEDUCT_TYPE_CHOICES = (("FD", "Full Deduct"), ("PD", "Part Deduct"), ("FXD", "Fix Deduct"))

    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    deduct_type = models.CharField(max_length=3, choices=DEDUCT_TYPE_CHOICES)
    fixed_amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} Rs".format(self.party.get_display_text, self.balance)

    def deduct_balance(self, amount):
        self.balance -= amount
        self.save()

    def get_part_deduct_amount(self, amount):
        return min(amount//3, self.balance)

    def get_payable_amount(self, amount):
        if self.deduct_type == "FXD":
            payable_amount = min(self.fixed_amount, self.balance, amount)
        elif self.deduct_type == "FD":
            payable_amount = min(amount, self.balance)
        else:
            payable_amount = self.get_part_deduct_amount(amount)
        return payable_amount, amount - payable_amount


class WalletAdvance(models.Model):

    # GATEWAY_CHOICES = (("CS", "Cash"), ("AC", "Account"))

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    gateway_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    gateway_id = models.PositiveIntegerField()
    gateway = GenericForeignKey("gateway_type", "gateway_id")

    created_on = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to="parties/wallets/advances/", blank=True, null=True)

    def __str__(self):
        return "{} - {} - {}".format(self.wallet.party.get_display_text, self.amount, self.gateway_type)
