from django.db import models
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError


class Material(models.Model):
    name = models.CharField(max_length=64)
    attribute = models.CharField(max_length=6, blank=True)
    material_code = models.CharField(max_length=12)
    extra_info = models.TextField(blank=True)
    has_report = models.BooleanField(default=False)
    merge_material = models.ForeignKey("self", related_name="merge_materials", on_delete=models.SET_NULL, blank=True, null=True)

    default_rate = models.FloatField(default=1.0)
    rate_gap = models.FloatField(default=1.0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

    @property
    def get_absolute_url(self):
        return reverse_lazy("materials:detail", kwargs={"material_code": self.material_code})

    def check_allowed_rate(self, amount):
        if amount < self.get_down_rate or amount > self.get_up_rate:
            return False
        return True

    @property
    def get_up_rate(self):
        return self.default_rate + self.rate_gap

    @property
    def get_down_rate(self):
        return max(0.0, (self.default_rate - self.rate_gap))

    @property
    def get_merge_material(self):
        return self.merge_material

    @property
    def get_merge_materials(self):
        return self.merge_materials.all()
