from django.db import models


class BankAccount(models.Model):
    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    acc_no = models.CharField(max_length=32)
    ifsc_code = models.CharField(max_length=32)
    bank_name = models.CharField(max_length=64)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.party.name, self.bank_name)

    @property
    def get_display_text(self):
        return "{} - {}".format(self.party.get_display_text, self.bank_name)
