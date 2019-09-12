from django.db import models


class Material(models.Model):
    name = models.CharField(max_length=64)
    attribute = models.CharField(max_length=6, blank=True)
    code = models.CharField(max_length=12)
    extra_info = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name
