from django.urls import reverse_lazy
from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from . import validators
from django.db.models import Sum, Count, Max, Min
from django.conf import settings
from django.db.models.signals import post_save, pre_save, m2m_changed
import decimal
from rates.models import GroupRate, RateGroup, IndividualRate


class Weight(models.Model):

    challan = models.ForeignKey("Challan", on_delete=models.CASCADE)
    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    weight_counts = models.CharField(max_length=254, validators=[validate_comma_separated_integer_list, ], default='')
    total_weight = models.FloatField(validators=[validators.validate_positive_float], default=0)
    rate_per_unit = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return "{} * {} kg = {}".format(self.material.get_display_text, self.total_weight, self.amount)

    class Meta:
        unique_together = ("challan", "material")

    @property
    def get_weight_counts_list(self):
        return map(float, self.weight_counts.split(",")[:-1])


def assign_total_weight_and_amount(sender, instance, *args, **kwargs):
    if instance.weight_counts != "":
        print("weight count not ''")
        total_weight = sum(instance.get_weight_counts_list)
        if instance.total_weight != total_weight:
            print("Total weight")
            instance.total_weight = total_weight
            instance.save()
        individual_rates = instance.challan.party.individualrate_set.filter(is_active=True, material=instance.material)
        if individual_rates.exists():
            rate = individual_rates.first()
        else:
            group_rates = instance.challan.party.rate_group.grouprate_set.filter(is_active=True, material=instance.material)
            if group_rates.exists():
                rate = group_rates.first()
            else:
                rate = None
        if rate is not None and instance.rate_per_unit != rate.amount:
            print("Rate not None")
            instance.rate_per_unit = rate.amount
            instance.save()
        amount = decimal.Decimal(instance.total_weight) * decimal.Decimal(instance.rate_per_unit)
        if instance.amount != amount:
            print("Amount not matching")
            instance.amount = amount
            instance.save()
    instance.challan.save()


post_save.connect(assign_total_weight_and_amount, sender=Weight)


def challan_no_generator():
    return "{}-{}".format(settings.BRANCH_ID, Challan.objects.count()+1)


class Challan(models.Model):

    PAYMENT_GATEWAY_TYPE = (("CS", "Cash"), ("AC", "Account"), ("AL", "Account Less"))
    payment_gateway_type = models.CharField(max_length=2, choices=PAYMENT_GATEWAY_TYPE)
    is_payed = models.BooleanField()

    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    challan_no = models.CharField(max_length=32, unique=True, default=challan_no_generator)

    weights_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    extra_charges = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    is_generated = models.BooleanField(default=False)
    image = models.ImageField(upload_to="payments/", blank=True, null=True)

    extra_info = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    generated_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.party.name

    @property
    def get_display_text(self):
        return self.challan_no

    @property
    def calculate_weights_amount(self):
        return self.weight_set.aggregate(amount=Sum("amount"))['amount']

    @property
    def get_update_url(self):
        return reverse_lazy("challans:update", kwargs={"challan_no": self.challan_no})


def assign_weights_amount(sender, instance, *args, **kwargs):
    if instance.weight_set.exists():
        weights_amount = instance.calculate_weights_amount
        if instance.weights_amount != weights_amount:
            instance.weights_amount = weights_amount
            instance.save()


post_save.connect(assign_weights_amount, sender=Challan)
