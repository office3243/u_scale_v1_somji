from django.db import models
from django.utils import timezone
from challans.models import Challan, Weight
from django.db.models import Min, Max, Sum, Q
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from loadings.models import Loading, LoadingWeight


def get_start_date():
    today = timezone.now().date()
    try:
        challan_date = Challan.objects.aggregate(min_date=Min("created_on"))['min_date'].date()
    except:
        challan_date = today
    try:
        loading_date = Loading.objects.aggregate(min_date=Min("created_on__date"))['min_date'].date()
    except:
        loading_date = today
    return min(challan_date, loading_date)


class MaterialStock(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    date = models.DateField(auto_created=True)
    updated_on = models.DateTimeField(auto_now=True)

    material = models.ForeignKey("materials.Material", on_delete=models.PROTECT)
    opening_weight = models.FloatField(default=0.0)
    in_weight = models.FloatField(default=0.0)
    out_weight = models.FloatField(default=0.0)
    closing_weight = models.FloatField(default=0.0)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return "{} - {} {}".format(self.date, self.material.get_display_text, self.opening_weight)

    @property
    def is_first_stock(self):
        if self.date <= get_start_date():
            return True
        return False

    @property
    def get_previous_stock(self):
        if self.is_first_stock:
            return None
        previous_stock = MaterialStock.objects.get_or_create(date=self.date-timezone.timedelta(days=1), material=self.material)[0]
        previous_stock.save()
        return previous_stock

    @property
    def calculate_opening_weight(self):
        previous_stock = self.get_previous_stock
        if previous_stock is not None:
            return previous_stock.closing_weight
        return 0.00

    #   Challans Section

    @property
    def get_challans(self):
        return Challan.objects.filter(created_on__date=self.date)

    @property
    def calculate_in_weight(self):
        in_weight = Weight.objects.filter(challan__in=self.get_challans, material=self.material).aggregate(total=Sum("stock_weight"))['total'] or 0.00
        return round(in_weight, 2)

    @property
    def check_challan_status(self):
        return not self.get_challans.filter(is_reports_done=False).exists()

    #   Loadings

    @property
    def get_loadings(self):
        return Loading.objects.filter(created_on__date=self.date)

    @property
    def calculate_out_weight(self):
        out_weight = LoadingWeight.objects.filter(loading__in=self.get_loadings, material=self.material).aggregate(total=Sum("weight_count"))['total'] or 0.00
        return round(out_weight, 2)

    @property
    def check_loading_status(self):
        return not self.get_loadings.exclude(status="DN").exists()

    #   ---------------------

    @property
    def check_previous_status(self):
        previous_stock = self.get_previous_stock
        if previous_stock is not None:
            return previous_stock.status == "DN"
        return True

    @property
    def calculate_closing_weight(self):
        return round((self.opening_weight + self.in_weight - self.out_weight), 2)

    @property
    def check_status(self):
        return "DN" if (self.check_challan_status and self.check_previous_status and self.check_loading_status) else "PN"


def assign_opening_weight(sender, instance, *args, **kwargs):
    if not instance.is_first_stock:
        opening_weight = instance.calculate_opening_weight
        if instance.opening_weight != opening_weight:
            instance.opening_weight = opening_weight
            instance.save()


def assign_in_weight(sender, instance, *args, **kwargs):
    in_weight = instance.calculate_in_weight
    if instance.in_weight != in_weight:
        instance.in_weight = in_weight
        instance.save()


def assign_out_weight(sender, instance, *args, **kwargs):
    out_weight = instance.calculate_out_weight
    if instance.out_weight != out_weight:
        instance.out_weight = out_weight
        instance.save()


def assign_closing_weight(sender, instance, *args, **kwargs):
    closing_weight = instance.calculate_closing_weight
    if instance.closing_weight != closing_weight:
        instance.closing_weight = closing_weight
        instance.save()


def assign_status(sender, instance, *args, **kwargs):
    status = instance.check_status
    if instance.status != status:
        instance.status = status
        instance.save()


post_save.connect(assign_opening_weight, sender=MaterialStock)
post_save.connect(assign_in_weight, sender=MaterialStock)
post_save.connect(assign_out_weight, sender=MaterialStock)
post_save.connect(assign_closing_weight, sender=MaterialStock)
post_save.connect(assign_status, sender=MaterialStock)
