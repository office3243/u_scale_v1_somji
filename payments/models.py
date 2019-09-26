from django.db import models


class AccountTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    pay = models.ForeignKey("Pay", on_delete=models.CASCADE)
    bank_account = models.ForeignKey("bank_accounts.BankAccount", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    payed_on = models.DateTimeField(auto_now_add=True)
    extra_info = models.TextField(blank=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.amount)


class CashTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    pay = models.ForeignKey("Pay", on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    payed_on = models.DateTimeField(auto_now_add=True)
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


class Pay(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.amount)


class Payment(models.Model):

    PAYMENT_MODE_CHOICES = (("FL", "Full Payment"), ("AL", "Account Less"))
    PAYMENT_STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.OneToOneField("challans.Challan", on_delete=models.CASCADE)

    mode = models.CharField(max_length=2, choices=PAYMENT_MODE_CHOICES)
    status = models.CharField(max_length=2, choices=PAYMENT_STATUS_CHOICES, default="PN")

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    payed_on = models.DateTimeField(blank=True, null=True)

    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return "{} - {} ({}) - ".format(self.challan.party.get_display_text, self.amount, self.get_status_display())
