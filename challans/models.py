from django.urls import reverse_lazy
from django.db import models
from django.core.validators import MinValueValidator
from . import validators
from django.db.models import Sum, Count, Max, Min
from django.conf import settings
from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
import decimal
from rates.models import RateGroup, GroupMaterialRate
import math
from django.contrib.auth.models import User


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


class ReportWeight(models.Model):

    REPORT_TYPE_CHOICES = (("RP", "Report"), ("RT", "Return"))
    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    weight = models.OneToOneField("Weight", on_delete=models.CASCADE)
    weight_count = models.FloatField(validators=[MinValueValidator(0.10), ],)
    report_type = models.CharField(max_length=2, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    reported_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {} - {}".format(self.weight.material.name, self.weight_count, self.get_report_type_display())


post_save.connect(save_signal_to_parent, sender=ReportWeight)
post_delete.connect(save_signal_to_parent, sender=ReportWeight)


class Weight(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.ForeignKey("Challan", on_delete=models.CASCADE)
    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
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
            return self.weightentry_set.aggregate(total_weight=Sum("entry"))['total_weight'] - self.get_report_weight
        return 0.00

    @property
    def get_report_weight(self):
        if hasattr(self, "reportweight"):
            return self.reportweight.weight_count
        else:
            return 0.0

    @property
    def get_default_rate(self):
        if self.challan.party.rate_group:
            try:
                return GroupMaterialRate.objects.get(material=self.material, rate_group=self.challan.party.rate_group).amount
            except:
                return decimal.Decimal(1)
        return decimal.Decimal(1)

    @property
    def get_report_weight_display(self):
        if hasattr(self, "reportweight"):
            return self.reportweight.weight_count
        else:
            return "-"

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


def assign_rate_per_unit(sender, instance, *args, **kwargs):
    if not instance.rate_per_unit:
        instance.rate_per_unit = instance.get_default_rate
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


def check_weight_status(sender, instance, *args, **kwargs):
    if hasattr(instance, "reportweight"):
        report_done = (instance.reportweight.status == "DN")
        if report_done and instance.status == "PN":
            instance.status = "DN"
            instance.save()
        elif not report_done and instance.status == "DN":
            instance.status = "PN"
            instance.save()
    elif instance.status == "PN":
        instance.status = "DN"
        instance.save()


def refresh_challan(sender, instance, *args, **kwargs):
    instance.refresh_challan()


post_save.connect(assign_rate_per_unit, sender=Weight)
post_save.connect(assign_total_weight, sender=Weight)
post_save.connect(assign_amount, sender=Weight)
post_save.connect(check_weight_status, sender=Weight)
post_save.connect(refresh_challan, sender=Weight)


class Challan(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    challan_no = models.CharField(max_length=32, blank=True, null=True)
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
    is_rates_assigned = models.BooleanField(default=False)
    is_payed = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return self.challan_no

    @property
    def get_display_text(self):
        return self.challan_no

    @property
    def get_challan_has_report(self):
        return self.weight_set.filter(material__has_report=True).exists()

    @property
    def get_materials_has_report(self):
        return self.weight_set.filter(material__has_report=True)

    @property
    def calculate_weights_amount(self):
        if self.weight_set.exists():
            return math.ceil(self.weight_set.aggregate(amount=Sum("amount"))['amount'])
        else:
            return 0.00

    @property
    def get_absolute_url(self):
        return reverse_lazy("challans:detail", kwargs={"challan_no": self.challan_no})

    @property
    def get_entries_url(self):
        return reverse_lazy("challans:entries", kwargs={'challan_no': self.challan_no})

    @property
    def get_assign_reports_url(self):
        return reverse_lazy("challans:assign_reports", kwargs={'challan_no': self.challan_no})

    @property
    def get_entries_submit_url(self):
        return reverse_lazy("challans:entries_submit", kwargs={"challan_no": self.challan_no})

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


def check_status(sender, instance, *args, **kwargs):
    all_done = all([instance.is_entries_done, instance.is_payed, instance.is_reports_done])
    if all_done and instance.status == "PN":
        instance.status = "DN"
        instance.save()
    if not all_done and instance.status == "DN":
        instance.status = "PN"
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
        if instance.payment.amount != instance.total_amount:
            instance.payment.amount = instance.total_amount
            instance.save()
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


def challan_no_generator(challan):
    return "{}{}".format(settings.CHALLAN_NO_PREFIX, challan.id)


def assign_challan_no(sender, instance, *args, **kwargs):
    challan_no = challan_no_generator(instance)
    if instance.challan_no != challan_no:
        instance.challan_no = challan_no
        instance.save()


post_save.connect(assign_challan_no, sender=Challan)

post_save.connect(assign_weights_amount, sender=Challan)
post_save.connect(check_reports_done, sender=Challan)
post_save.connect(check_is_payed, sender=Challan)
post_save.connect(check_status, sender=Challan)
