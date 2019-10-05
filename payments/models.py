from django.db import models
from django.db.models.signals import post_save
from django.db.models import Sum, Max, Count
from django.core.validators import ValidationError
from decimal import Decimal
from itertools import chain
from operator import attrgetter
from django.conf import settings


def save_payment(sender, instance, *args, **kwargs):
    instance.payment.save()


class AccountTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    unique_id = models.CharField(max_length=32, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    bank_account = models.ForeignKey("bank_accounts.BankAccount", on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    payed_on = models.DateTimeField(blank=True, null=True)
    extra_info = models.TextField(blank=True)
    photo = models.ImageField(upload_to="payments/account_transactions/photos/", blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.amount)


def assign_unique_id(sender, instance, *args, **kwargs):
    if not instance.unique_id and instance.status == "DN":
        instance.unique_id = "{}-{}".format(settings.BRANCH_AC_PAYMENT_PREFIX, AccountTransaction.objects.count()+1)


post_save.connect(assign_unique_id, sender=AccountTransaction)
post_save.connect(save_payment, sender=AccountTransaction)


class CashTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    payed_on = models.DateTimeField(blank=True, null=True)
    extra_info = models.TextField(blank=True)
    photo = models.ImageField(upload_to="payments/account_transactions/photos/", blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="DN")

    def __str__(self):
        return str(self.amount)


post_save.connect(save_payment, sender=CashTransaction)


class WalletTransaction(models.Model):

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    wallet = models.ForeignKey("parties.Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)

    def re_add_amount(self):
        self.wallet.add_balance(amount=self.amount)

    def __str__(self):
        return str(self.amount)


def deduct_from_wallet(sender, created, instance, *args, **kwargs):
    if not instance.amount <= instance.wallet.balance:
        instance.delete()
    if created:
        instance.wallet.deduct_balance(amount=instance.amount)


post_save.connect(deduct_from_wallet, sender=WalletTransaction)
post_save.connect(save_payment, sender=WalletTransaction)


class Payment(models.Model):
    PAYMENT_MODE_CHOICES = (("DP", "Direct Payment"), ("AL", "Account Less"))
    PAYMENT_STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.OneToOneField("challans.Challan", on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=2, choices=PAYMENT_MODE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=2, choices=PAYMENT_STATUS_CHOICES, default="PN")
    payed_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    payed_on = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return "{} - {} ({}) - ".format(self.challan.party.get_display_text, self.amount, self.get_status_display())

    @property
    def get_transactions_sum(self):
        return sum([
            (self.accounttransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)),
            (self.cashtransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)),
            (self.wallettransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)),
        ])

    @property
    def calculate_payed_amount(self):
        return sum([
            self.accounttransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00),
            self.cashtransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00),
            self.wallettransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00),
        ])

    @property
    def get_remaining_amount(self):
        return self.amount - self.payed_amount

    @property
    def get_is_wallet_payed(self):
        print(self.wallettransaction_set.exists())
        return self.wallettransaction_set.exists()

    def validate_amounts(self):
        """validate all transaction amounts with total"""
        transactions_sum = self.get_transactions_sum
        if transactions_sum > self.amount:
            raise ValidationError("Paying amount cannot be greater than Actual amount")

    def clean(self):
        super().clean()
        self.validate_amounts()


def assign_payment_mode(sender, instance, *args, **kwargs):
    if instance.status == "PN":
        payment_mode = "AL" if instance.challan.party.wallet_set.filter(is_active=True).exists() else "DP"
        if instance.payment_mode != payment_mode:
            instance.payment_mode = payment_mode
            instance.save()


def assign_amount(sender, instance, *args, **kwargs):
    challan_amount = instance.challan.total_amount
    if instance.amount != challan_amount:
        instance.amount = challan_amount
        instance.save()


def assign_payed_amount(sender, instance, *args, **kwargs):
    payed_amount = instance.calculate_payed_amount
    if instance.payed_amount != payed_amount:
        instance.payed_amount = payed_amount
        instance.save()


def check_payment_status(sender, instance, *args, **kwargs):
    ac_tr_pending = instance.accounttransaction_set.filter(status="PN").exists()

    if (instance.amount != instance.payed_amount or ac_tr_pending) and instance.status == "DN" and instance.challan.is_reports_done:
        instance.status = "PN"
        print(5)
        instance.save()
    elif instance.amount == instance.payed_amount and instance.status == "PN" and not instance.challan.is_reports_done and not ac_tr_pending:
        print(6)
        instance.status = "DN"
        instance.save()


def refresh_challan(sender, instance, *args, **kwargs):
    instance.challan.save()


def clean_payment(sender, instance, *agrs, **kwargs):
    print("Full Clean")
    instance.full_clean()


post_save.connect(assign_payment_mode, sender=Payment)
post_save.connect(assign_amount, sender=Payment)
post_save.connect(clean_payment, sender=Payment)
post_save.connect(assign_payed_amount, sender=Payment)
post_save.connect(check_payment_status, sender=Payment)
post_save.connect(refresh_challan, sender=Payment)
