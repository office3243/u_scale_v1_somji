from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings
from django.urls import reverse_lazy
from django.core.validators import ValidationError


class Party(models.Model):

    RATE_TYPE_CHOICES = (("GR", "Group Rate"), ("IR", "Individual Rate"))

    rate_type = models.CharField(max_length=2, choices=RATE_TYPE_CHOICES)
    rate_group = models.ForeignKey("rates.RateGroup", on_delete=models.PROTECT, blank=True, null=True)

    name = models.CharField(max_length=128)
    party_code = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=13)
    whatsapp = models.CharField(max_length=13, blank=True)
    email = models.EmailField(blank=True, null=True)
    extra_info = models.TextField(blank=True)

    is_wallet_party = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.party_code

    @property
    def get_absolute_url(self):
        return reverse_lazy("parties:detail", kwargs={"party_code": self.party_code})

    @property
    def get_update_url(self):
        return reverse_lazy("parties:update", kwargs={"party_code": self.party_code})

    @property
    def get_challan_ad_url(self):
        return str(reverse_lazy("challans:add")) + "?ptid={}".format(self.id)

    @property
    def get_wallet(self):
        if self.wallet_set.filter(is_active=True).exists():
            return self.wallet_set.filter(is_active=True).first()
        else:
            return None

    @property
    def get_bank_account_add_url(self):
        return str(reverse_lazy("bank_accounts:add")) + "?ptid={}".format(self.id)

    @property
    def get_bank_accounts(self):
        return self.bankaccount_set.filter(is_active=True)

    def clean(self):
        super().clean()
        if self.id:
            if self.rate_type == "GR" and not self.rate_group:
                raise ValidationError("Rate Group is must for party with Group Rate Type")

    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"


def party_code_generator(party):
    return "{}{}".format(settings.PARTY_CODE_PREFIX, party.id)


def assign_party_code(sender, instance, *args, **kwargs):
    party_code = party_code_generator(instance)
    if instance.party_code != party_code:
        instance.party_code = party_code
        instance.save()


def create_party_wallet(sender, instance, *args, **kwargs):
    if instance.is_wallet_party and not instance.wallet_set.filter(is_active=True).exists():
        Wallet.objects.create(party=instance)


post_save.connect(assign_party_code, sender=Party)
post_save.connect(create_party_wallet, sender=Party)


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
        if self.is_active:
            self.balance -= amount
            self.save()
            return self.balance

    def add_balance(self, amount):
        if self.is_active:
            self.balance += amount
            self.save()
            return self.balance

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

    GATEWAY_CHOICES = (("CS", "Cash"), ("AC", "Account"), ("IP", "In Payment"))

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    gateway = models.CharField(max_length=2, choices=GATEWAY_CHOICES, default="CS")

    created_on = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to="parties/wallets/advances/", blank=True, null=True)

    def __str__(self):
        return "{} - {} - {}".format(self.wallet.party.get_display_text, self.amount, self.gateway)

    def add_to_wallet(self, amount):
        self.wallet.add_balance(amount=amount)

    def refund_amount(self, amount):

        self.wallet.deduct_balance(amount=amount)


def add_amount_to_wallet(sender, instance, created, *args, **kwargs):
    if created:
        instance.add_to_wallet(amount=instance.amount)


def refund_on_delete(sender, instance, *args, **kwargs):
    instance.refund_amount(instance.amount)
    instance.delete()


post_save.connect(add_amount_to_wallet, sender=WalletAdvance)
post_delete.connect(add_amount_to_wallet, sender=WalletAdvance)
