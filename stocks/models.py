from django.db import models
import datetime
from challans.models import Challan


def get_start_date():
    try:
        return Challan.objects.first("")


class MaterialStock(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    date = models.DateField(auto_created=True)
    updated_on = models.DateTimeField(auto_now=True)

    material = models.ForeignKey("materials.Material", on_delete=models.PROTECT)
    opening_weight = models.FloatField(blank=True, null=True)
    closing_weight = models.FloatField(blank=True, null=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return "{} - {} {}".format(self.date, self.material.get_display_text, self.opening_weight)

    @property
    def get_previous_stock(self):
        stock = MaterialStock.objects.get_or_create(date=self.date-datetime.timedelta(days=1))
        return stock

    @property
    def get_opening_weight(self):
        previous_stock = self.get_previous_stock
        return previous_stock.closing_weight


# def check_previous_stock(sender, instance, *args, **kwargs):
#     previous_stock = instance.get_previous_stock
#     if not previous_stock:
#         MaterialStock.objects.create(date=instance.date-datetime.timedelta(days=1))


def assign_opening_weight(sender, instance, *args, **kwargs):
    opening_weight = instance.get_opening_weight
    if instance.opening_weight != opening_weight:
        instance.opening_weight = opening_weight
        instance.save()
