from django.db import models


class BankAccount(models.Model):
    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    acc_no = models.CharField(max_length=32)
    ifsc_code = models.CharField(max_length=32)
    branch_name = models.CharField(max_length=64)
    bank_name = models.CharField(max_length=64)

    def __str__(self):
        return "{} - {}".format(self.party.name, self.bank_name)
