from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator


class BankAccount(models.Model):
    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    account_holder = models.CharField(max_length=128)
    acc_no = models.CharField(max_length=32)
    ifsc_code = models.CharField(max_length=11, validators=[MinLengthValidator(limit_value=11)])
    bank_name = models.CharField(max_length=64)
    branch_name = models.CharField(max_length=64, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.party.name, self.bank_name)

    @property
    def get_display_text(self):
        return "{} - {}".format(self.party.get_display_text, self.bank_name)
