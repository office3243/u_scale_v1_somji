from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class CashTransaction(models.Model):

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)


class AccountTransaction(models.Model):

    bank_account = models.ForeignKey("bank_accounts.BankAccount", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    created_on = models.DateTimeField(auto_now_add=True)

    extra_info = models.TextField(blank=True)

    def __str__(self):
        return str(self.amount)


class WalletTransaction(models.Model):

    wallet = models.ForeignKey("parties.Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    is_full_amount = models.BooleanField()
    remaining_amount = models.DecimalField(max_digits=9, decimal_places=2)

    gateway_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    gateway_id = models.PositiveIntegerField()
    gateway = GenericForeignKey("gateway_type", "gateway_id")

    def __str__(self):
        return str(self.amount)


class Payment(models.Model):

    challan = models.OneToOneField("challans.Challan", on_delete=models.CASCADE)

    gateway_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    gateway_id = models.PositiveIntegerField(blank=True, null=True)
    gateway = GenericForeignKey("gateway_type", "gateway_id")

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    is_payed = models.BooleanField(default=False)
    payed_on = models.DateTimeField(blank=True, null=True)

    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return "{} - {} ({}) - ".format(self.challan.party.get_display_text, self.amount, self.challan.get_display_text, self.gateway_type)
