from django.db import models


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

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"
