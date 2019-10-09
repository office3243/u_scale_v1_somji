from django.contrib import admin
from .models import WeightEntry, Weight, Challan, ReportWeight

admin.site.register(ReportWeight)
admin.site.register(WeightEntry)
admin.site.register(Weight)
admin.site.register(Challan)
