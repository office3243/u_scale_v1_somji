from django.db import models
from django.core.exceptions import ValidationError


class RateGroup(models.Model):

    name = models.CharField(max_length=64)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name


class MaterialRate(models.Model):

    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    rate_group = models.ForeignKey(RateGroup, on_delete=models.CASCADE)
    parties = models.ManyToManyField("parties.Party")

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    extra_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} (Group {}({}) and {} Individual Parties)".format(self.material.get_display_text, self.amount,
                                                                         self.rate_group.get_display_text,
                                                                         self.rate_group.party_set.count(),
                                                                         self.parties.count())

    def clean(self):
        super().clean()
        for party in self.parties.all():
            if party.materialrate_set.filter(material=self.material).exclude(id=self.id).count() > 0:
                raise ValidationError("A Party may occur in only one Rate for a material!")

    class Meta:
        unique_together = ("material", "rate_group")

