from django.urls import reverse_lazy
from django.db import models
from django.core.validators import MinValueValidator
from . import validators
from django.db.models import Sum, Count, Max, Min
from django.conf import settings
from django.db.models.signals import post_save, pre_save, m2m_changed
import decimal
from rates.models import RateGroup, MaterialRate


class WeightEntry(models.Model):

    weight = models.ForeignKey("Weight", on_delete=models.CASCADE)
    entry = models.FloatField(validators=[MinValueValidator(0.10), ],)

    def __str__(self):
        return str(self.entry)

    class Meta:
        verbose_name_plural = "Weight Entries"


def save_signal_to_parent(sender, instance, *args, **kwargs):
    """to send signal to parent model Weight on each save"""
    return instance.weight.save()


post_save.connect(save_signal_to_parent, sender=WeightEntry)


class Weight(models.Model):

    challan = models.ForeignKey("Challan", on_delete=models.CASCADE)
    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)

    report_weight = models.FloatField(default=0.00)

    total_weight = models.FloatField(validators=[MinValueValidator(0.00)], default=0.00)
    rate_per_unit = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} * {} kg = {}".format(self.material.get_display_text, self.total_weight, self.amount)

    class Meta:
        unique_together = ("challan", "material")

    @property
    def calculate_total_weight(self):
        """to return sum of all weight entries in relation. if not exists return 0.00"""
        if self.weightentry_set.exists():
            return self.weightentry_set.aggregate(total_weight=Sum("entry"))['total_weight'] - self.report_weight
        return 0.00

    @property
    def calculate_rate(self):
        return 10.00

    @property
    def calculate_amount(self):
        return self.rate_per_unit * decimal.Decimal(self.total_weight)

    @property
    def get_recent_entry(self):
        return self.weightentry_set.last()


def assign_changed_fields(sender, instance, *args, **kwargs):
    """to assign weight, rate and amount of weight model on each save"""
    calculated_weight = decimal.Decimal(instance.calculate_total_weight)
    if instance.total_weight != calculated_weight:
        instance.total_weight = calculated_weight
        instance.save()
    if instance.rate_per_unit == 0.00:
        calculated_rate = decimal.Decimal(instance.calculate_rate)
        instance.rate_per_unit = calculated_rate
        instance.save()
    calculated_amount = instance.calculate_amount
    if instance.amount != calculated_amount:
        instance.amount = calculated_amount
        instance.save()
    instance.challan.save()


post_save.connect(assign_changed_fields, sender=Weight)


def challan_no_generator():
    return "{}-{}".format(settings.BRANCH_ID, Challan.objects.count()+1)


class Challan(models.Model):

    STATUS_CHOICES = (("CR", "Created"), ("ED", "Entries Done"), ("RD", "Reports Done"),
                      ("PB", "Published"), ("PD", "Payment Done"))

    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    challan_no = models.CharField(max_length=32, unique=True, default=challan_no_generator)

    vehicle_details = models.CharField(max_length=128, blank=True, null=True)

    weights_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    extra_charges = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    status = models.CharField(max_length=2, default="CR")
    image = models.ImageField(upload_to="payments/", blank=True, null=True)

    extra_info = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.party.name

    @property
    def get_display_text(self):
        return self.challan_no

    @property
    def calculate_weights_amount(self):
        if self.weight_set.exists():
            return self.weight_set.aggregate(amount=Sum("amount"))['amount']
        else:
            return 0.00

    @property
    def get_entries_url(self):
        return reverse_lazy("challans:entries", kwargs={'challan_no': self.challan_no})

    @property
    def get_update_url(self):
        return reverse_lazy("challans:update", kwargs={"challan_no": self.challan_no})

    @property
    def get_payment_add_url(self):
        return reverse_lazy("payments:add", kwargs={"challan_no": self.challan_no})

    @property
    def get_done_url(self):
        return reverse_lazy("challans:done", kwargs={"challan_no": self.challan_no})

    @property
    def get_recent_weight_entry(self):
        return self.weight_set.latest("updated_on").get_recent_entry

    @property
    def get_payable_amount(self):
        return self.total_amount


def assign_weights_amount(sender, instance, *args, **kwargs):
    """to assign all weights amount on each save"""
    weights_amount = instance.calculate_weights_amount
    if instance.weights_amount != weights_amount:
        instance.weights_amount = weights_amount
        instance.total_amount = weights_amount + instance.extra_charges
        instance.save()
    total_amount = instance.weights_amount + instance.extra_charges
    if instance.total_amount != total_amount:
        instance.total_amount = total_amount
        instance.save()


post_save.connect(assign_weights_amount, sender=Challan)
