from django.contrib import admin
from .models import WeightEntry, Weight, Challan, ReportWeight


class WeightInline(admin.StackedInline):
    model = Weight
    extra = 0


class ChallanAdmin(admin.ModelAdmin):

    list_display = ("challan_no", "party", "weights_amount", "created_on", "status")
    inlines = [WeightInline, ]
    readonly_fields = ("created_on", "updated_on")


class WeightAdmin(admin.ModelAdmin):

    list_display = ("material", "rate_per_unit", "total_weight", "stock_weight", "challan")
    list_filter = ("challan", "material", "challan__created_on")


class ReportWeightAdmin(admin.ModelAdmin):

    list_filter = ("weight__material", "weight__challan", "weight__challan__party")
    list_display = ("weight", "weight_count", "report_type")


class WeightEntryAdmin(admin.ModelAdmin):

    list_display = ("entry", "weight")
    list_filter = ("weight__material", "weight__challan")


admin.site.register(ReportWeight, ReportWeightAdmin)
admin.site.register(WeightEntry, WeightEntryAdmin)
admin.site.register(Weight, WeightAdmin)
admin.site.register(Challan, ChallanAdmin)
