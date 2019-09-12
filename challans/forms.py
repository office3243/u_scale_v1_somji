from django import forms
from .models import Challan


class ChallanRawCreateForm(forms.ModelForm):

    class Meta:
        model = Challan
        fields = ("party", )
