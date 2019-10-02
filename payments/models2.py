# from django.db import models
# from django.db.models.signals import post_save
# from django.db.models import Sum, Max, Count
# from django.core.validators import ValidationError
# from decimal import Decimal
# from itertools import chain
# from operator import attrgetter
#
#
# class AccountTransaction(models.Model):
#     STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))
#
#     payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
#     bank_account = models.ForeignKey("bank_accounts.BankAccount", on_delete=models.CASCADE, blank=True, null=True)
#     amount = models.DecimalField(max_digits=9, decimal_places=2)
#     created_on = models.DateTimeField(auto_now_add=True)
#     payed_on = models.DateTimeField(blank=True, null=True)
#     extra_info = models.TextField(blank=True)
#     photo = models.ImageField(upload_to="payments/account_transactions/photos/", blank=True, null=True)
#     status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")
#
#     def __str__(self):
#         return str(self.amount)
#
#
# class CashTransaction(models.Model):
#     STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))
#
#     payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=9, decimal_places=2)
#     created_on = models.DateTimeField(auto_now_add=True)
#     payed_on = models.DateTimeField(blank=True, null=True)
#     extra_info = models.TextField(blank=True)
#     photo = models.ImageField(upload_to="payments/account_transactions/photos/", blank=True, null=True)
#     status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="DN")
#
#     def __str__(self):
#         return str(self.amount)
#
#
# class WalletTransaction(models.Model):
#     payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
#     wallet = models.ForeignKey("parties.Wallet", on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=9, decimal_places=2)
#     created_on = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return str(self.amount)
#
#
# def deduct_from_wallet(sender, created, instance, *args, **kwargs):
#     if not instance.amount <= instance.wallet.balance:
#         instance.delete()
#     if created:
#         instance.wallet.deduct_balance(amount=instance.amount)
#
#
# post_save.connect(deduct_from_wallet, sender=WalletTransaction)
#
#
# class Payment(models.Model):
#     PAYMENT_MODE_CHOICES = (("DP", "Direct Payment"), ("AL", "Account Less"))
#     PAYMENT_STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))
#
#     challan = models.OneToOneField("challans.Challan", on_delete=models.CASCADE)
#     payment_mode = models.CharField(max_length=2, choices=PAYMENT_MODE_CHOICES)
#     status = models.CharField(max_length=2, choices=PAYMENT_STATUS_CHOICES, default="PN")
#     payed_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
#     amount = models.DecimalField(max_digits=9, decimal_places=2)
#     payed_on = models.DateTimeField(blank=True, null=True)
#     image = models.ImageField(upload_to="payments/", blank=True, null=True)
#     extra_info = models.TextField(blank=True)
#
#     def __str__(self):
#         return "{} - {} ({}) - ".format(self.challan.party.get_display_text, self.amount, self.get_status_display())
#
#     @property
#     def get_transactions_sum(self):
#         return sum([
#             (self.accounttransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)),
#             (self.cashtransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)),
#             (self.wallettransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)),
#         ])
#
#     @property
#     def calculate_payed_amount(self):
#         return sum([
#             self.accounttransaction_set.filter(status="DN").aggregate(total=Sum("amount"))["total"] or Decimal(0.00),
#             self.cashtransaction_set.filter(status="DN").aggregate(total=Sum("amount"))["total"] or Decimal(0.00),
#             self.wallettransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00),
#         ])
#
#     # @property
#     # def get_recent_transaction(self):
#     #     # l = self.accounttransaction_set.all().union(self.wallettransaction_set.all()).union(self.wallettransaction_set.all())
#     #     pending_transactions = sorted(
#     #         chain(self.accounttransaction_set.filter(status="PN"), self.wallettransaction_set.all(), self.cashtransaction_set.filter(status="PN")),
#     #         key=lambda instance: instance.id)
#     #     if pending_transactions:
#     #         return pending_transactions[0]
#
#     def validate_amounts(self):
#         """validate all transaction amounts with total"""
#         transactions_sum = self.get_transactions_sum
#         if transactions_sum > self.amount:
#             raise ValidationError("Paying amount cannot be greater than Actual amount")
#
#     def clean(self):
#         super().clean()
#         self.validate_amounts()
#
#
# def assign_payed_amount(sender, instance, *args, **kwargs):
#     payed_amount = instance.calculate_payed_amount
#     if instance.payed_amount != payed_amount:
#         instance.payed_amount = payed_amount
#         instance.save()
#
#
# # def validate_paying_amount(sender, instance, *args, **kwargs):
# #     paying_amount = instance.get_transactions_sum
# #     if paying_amount > instance.amount:
# #         recent_transaction = instance.get_recent_transaction
# #         recent_transaction.amount -= (paying_amount - instance.amount)
# #         recent_transaction.save()
# #         instance.save()
#
#
# def check_payment_status(sender, instance, *args, **kwargs):
#     payed_amount = instance.get_payed_amount
#     if instance.amount != payed_amount and instance.status == "DN":
#         instance.status = "PN"
#         instance.save()
#     elif instance.amount == payed_amount and instance.status == "PN":
#         instance.status = "DN"
#         instance.save()
#
#
# post_save.connect(assign_payed_amount, sender=Payment)
# # post_save.connect(validate_paying_amount, sender=Payment)
# post_save.connect(check_payment_status, sender=Payment)
