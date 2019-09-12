from django.contrib import admin
from .models import RateGroup, GroupRate, IndividualRate


admin.site.register(RateGroup)

admin.site.register(GroupRate)
admin.site.register(IndividualRate)
