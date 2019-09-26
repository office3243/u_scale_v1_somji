from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from challans.models import Challan


@login_required
def add(request, challan_no):

    challan = get_object_or_404(Challan, challan_no=challan_no)
    if request.method == "POST":
        pass
    else:
        context = {"challan": challan}
        return render(request, "payments/add.html", context)
