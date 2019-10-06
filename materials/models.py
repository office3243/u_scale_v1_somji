from django.db import models
from django.urls import reverse_lazy


class Material(models.Model):
    name = models.CharField(max_length=64)
    attribute = models.CharField(max_length=6, blank=True)
    material_code = models.CharField(max_length=12)
    extra_info = models.TextField(blank=True)
    has_report = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

    @property
    def get_absolute_url(self):
        return reverse_lazy("materials:detail", kwargs={"material_code": self.material_code})
