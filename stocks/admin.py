from django.contrib import admin
from .models import MaterialStock


class MaterialStockAdmin(admin.ModelAdmin):

    list_display = ("date", "material", "opening_weight", "in_weight", "out_weight", "closing_weight")

    list_filter = ("date", "material")

admin.site.register(MaterialStock, MaterialStockAdmin)
