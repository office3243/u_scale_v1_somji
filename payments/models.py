from django.db import models
from django.db.models.signals import post_save
from django.db.models import Sum, Max, Count
from django.core.validators import ValidationError


class AccountTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    bank_account = models.ForeignKey("bank_accounts.BankAccount", on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    payed_on = models.DateTimeField(blank=True, null=True)
    extra_info = models.TextField(blank=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.amount)


class CashTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    payed_on = models.DateTimeField(blank=True, null=True)
    extra_info = models.TextField(blank=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.amount)


class WalletTransaction(models.Model):

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)

    wallet = models.ForeignKey("parties.Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)

    is_full_amount = models.BooleanField()

    def __str__(self):
        return str(self.amount)


def deduct_from_wallet(sender, created, instance, *args, **kwargs):
    if created:
        instance.wallet.deduct_balance(amount=instance.amount)


post_save.connect(deduct_from_wallet, sender=WalletTransaction)


class Payment(models.Model):

    # acless or non-acless in pyament mode choice- need to think

    PAYMENT_MODE_CHOICES = (("DP", "Direct Payment"), ("AL", "Account Less"))
    PAYMENT_STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.OneToOneField("challans.Challan", on_delete=models.CASCADE)

    payment_mode = models.CharField(max_length=2, choices=PAYMENT_MODE_CHOICES, null=True)
    status = models.CharField(max_length=2, choices=PAYMENT_STATUS_CHOICES, default="PN")

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    payed_on = models.DateTimeField(blank=True, null=True)

    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return "{} - {} ({}) - ".format(self.challan.party.get_display_text, self.amount, self.get_status_display())

    @property
    def get_transactions_sum(self):
        total_amount = self.accounttransaction_set.aggregate(total=Sum("amount"))["total"] + \
                       self.cashtransaction_set.aggregate(total=Sum("amount"))["total"] + \
                       self.wallettransaction_set.aggregate(total=Sum("amount"))["total"]
        print(total_amount)
        return total_amount

    def validate_amounts(self):
        """validate all transaction amounts with total"""
        transactions_sum = self.get_transactions_sum
        if transactions_sum > self.amount:
            raise ValidationError("Paying amount cannot be greater than Actual amount")

    def clean(self):
        super().clean()
        self.validate_amounts()
