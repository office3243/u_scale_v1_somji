from django.contrib import admin
from .models import WeightEntry, Weight, Challan, ReportWeight


class WeightInline(admin.StackedInline):
    model = Weight
    extra = 0


class ChallanAdmin(admin.ModelAdmin):
    inlines = [WeightInline, ]


admin.site.register(ReportWeight)
admin.site.register(WeightEntry)
admin.site.register(Weight)
admin.site.register(Challan, ChallanAdmin)
