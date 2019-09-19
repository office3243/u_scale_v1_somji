from django import forms
from .models import Challan, Weight


class ChallanRawCreateForm(forms.ModelForm):

    class Meta:
        model = Challan
        fields = ("party", )


class WeightForm(forms.ModelForm):

    class Meta:
        model = Weight
        fields = ("rate_per_unit", )
