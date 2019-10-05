from django.urls import reverse_lazy
from django.db import models
from django.core.validators import MinValueValidator
from . import validators
from django.db.models import Sum, Count, Max, Min
from django.conf import settings
from django.db.models.signals import post_save, pre_save, m2m_changed
import decimal
from rates.models import RateGroup, MaterialRate
import math


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

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.ForeignKey("Challan", on_delete=models.CASCADE)
    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    report_weight = models.FloatField(blank=True, null=True)
    total_weight = models.FloatField(validators=[MinValueValidator(0.00)], default=0.00)
    rate_per_unit = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    updated_on = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return "{} * {} kg = {}".format(self.material.get_display_text, self.total_weight, self.amount)

    class Meta:
        unique_together = ("challan", "material")

    @property
    def calculate_total_weight(self):
        """to return sum of all weight entries in relation. if not exists return 0.00"""
        if self.weightentry_set.exists():
            return self.weightentry_set.aggregate(total_weight=Sum("entry"))['total_weight'] - (self.report_weight or 0.00)
        return 0.00

    @property
    def get_report_weight_display(self):
        return self.report_weight if self.report_weight is not None else "-"

    @property
    def get_default_rate(self):
        return 10.00

    @property
    def calculate_amount(self):
        if self.rate_per_unit:
            return self.rate_per_unit * decimal.Decimal(self.total_weight)
        return decimal.Decimal(0.00)

    @property
    def get_recent_entry(self):
        return self.weightentry_set.last()

    def refresh_challan(self):
        self.challan.save()


def assign_changed_fields(sender, instance, *args, **kwargs):
    """to assign weight, rate and amount of weight model on each save"""
    calculated_weight = decimal.Decimal(instance.calculate_total_weight)
    if instance.total_weight != calculated_weight:
        instance.total_weight = calculated_weight
        instance.save()
    if instance.rate_per_unit == 0.00:
        calculated_rate = decimal.Decimal(instance.get_default_rate)
        instance.rate_per_unit = calculated_rate
        instance.save()
    calculated_amount = instance.calculate_amount
    if instance.amount != calculated_amount:
        instance.amount = calculated_amount
        instance.save()
    instance.challan.save()


def assign_rate_per_unit(sender, instance, *args, **kwargs):
    if not instance.rate_per_unit:
        instance.rate_per_unit = instance
        instance.save()


def assign_total_weight(sender, instance, *args, **kwargs):
    total_weight = instance.calculate_total_weight
    if instance.total_weight != total_weight:
        instance.total_weight = total_weight
        instance.save()


def assign_amount(sender, instance, *args, **kwargs):
    amount = instance.calculate_amount
    if instance.amount != amount:
        instance.amount = amount
        instance.save()


def check_status(sender, instance, *args, **kwargs):
    print("Weight Check Status")
    if instance.report_weight is not None and instance.status == "PN":
        instance.status = "DN"
        instance.save()
    elif instance.report_weight is None and instance.status == "DN":
        instance.status = "PN"
        instance.save()


def refresh_challan(sender, instance, *args, **kwargs):
    instance.refresh_challan()


post_save.connect(assign_rate_per_unit, sender=Weight)
post_save.connect(assign_total_weight, sender=Weight)
post_save.connect(assign_amount, sender=Weight)
post_save.connect(check_status, sender=Weight)
post_save.connect(refresh_challan, sender=Weight)


def challan_no_generator():
    return "{}-{}".format(settings.BRANCH_ID, Challan.objects.count()+1)


class Challan(models.Model):

    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    challan_no = models.CharField(max_length=32, unique=True, default=challan_no_generator)
    vehicle_details = models.CharField(max_length=128, blank=True, null=True)
    weights_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    extra_charges = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    is_entries_done = models.BooleanField(default=False)
    is_reports_done = models.BooleanField(default=False)
    is_payed = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.party.name

    @property
    def get_display_text(self):
        return self.challan_no

    @property
    def calculate_weights_amount(self):
        if self.weight_set.exists():
            return math.ceil(self.weight_set.aggregate(amount=Sum("amount"))['amount'])
        else:
            return 0.00

    @property
    def get_entries_url(self):
        return reverse_lazy("challans:entries", kwargs={'challan_no': self.challan_no})

    @property
    def get_assign_reports_url(self):
        return reverse_lazy("challans:assign_reports", kwargs={'challan_no': self.challan_no})

    @property
    def get_entries_done_url(self):
        return reverse_lazy("challans:entries_done", kwargs={"challan_no": self.challan_no})

    @property
    def get_assign_rates_url(self):
        return reverse_lazy("challans:assign_rates", kwargs={'challan_no': self.challan_no})

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

    def refresh_weights(self):
        for weight in self.weight_set.all():
            weight.save()


def check_is_done(sender, instance, *args, **kwargs):
    all_done = all([instance.is_entries_done, instance.is_payed, instance.is_reports_done])
    if all_done and not instance.is_done:
        instance.is_done = True
        instance.save()
    if not all_done and instance.is_done:
        instance.is_done = False
        instance.save()


def check_reports_done(sender, instance, *agrs, **kwargs):
    if instance.weight_set.filter(status="PN").exists() and instance.is_reports_done:
        instance.is_reports_done = False
        instance.save()
    elif not instance.weight_set.filter(status="PN").exists() and not instance.is_reports_done:
        instance.is_reports_done = True
        instance.save()


def check_is_payed(sender, instance, *agrs, **kwargs):
    if hasattr(instance, "payment"):
        if instance.payment.status == "DN" and not instance.is_payed:
            instance.is_payed = True
            instance.save()
        elif instance.payment.status == "PN" and instance.is_payed:
            instance.is_payed = False
            instance.save()


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
post_save.connect(check_reports_done, sender=Challan)
post_save.connect(check_is_payed, sender=Challan)
post_save.connect(check_is_done, sender=Challan)
