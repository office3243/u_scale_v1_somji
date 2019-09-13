from django.shortcuts import render, get_object_or_404, redirect
from .models import Challan, Weight
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from materials.models import Material
from parties.models import Party
from django.http import JsonResponse
from .forms import ChallanRawCreateForm
from django.forms import modelformset_factory, inlineformset_factory


@login_required
def challan_create(request):
    if request.method == "POST":
        pass
    else:
        materials = Material.objects.filter(is_active=True)
        parties = Party.objects.filter(is_active=True)
        context = {'materials': materials, "parties": parties}
        return render(request, "challans/create.html", context)


@login_required
def challan_update(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    if request.method == "POST":
        pass
    else:
        materials = Material.objects.filter(is_active=True)
        parties = Party.objects.filter(is_active=True)
        context = {'materials': materials, "parties": parties, "challan": challan}
        return render(request, "challans/update.html", context)


@login_required
def challan_preview_update(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)

    WeightFormSet = inlineformset_factory(Challan, Weight, fields=("material", "weight_counts", "rate_per_unit", "amount"), extra=1)
    if request.method == "POST":
        formset = WeightFormSet(request.POST, instance=challan)
        if formset.is_valid():
            formset.save()
            return redirect("challans:preview_update", challan_no=challan_no)
    formset = WeightFormSet(instance=challan)
    materials = Material.objects.filter(is_active=True)
    parties = Party.objects.filter(is_active=True)
    context = {'materials': materials, "parties": parties, "challan": challan, "formset": formset}
    return render(request, "challans/preview_update.html", context)


class ChallanCreateView(LoginRequiredMixin, CreateView):

    model = Challan
    template_name = "challans/create.html"
    fields = "__all__"
    success_url = reverse_lazy("portal:home")


def weight_create(request):
    if request.method == "POST":
        challan_no = request.POST['challan_no']
        weight_count = float(request.POST['weight_count'])
        material_id = int(request.POST['material_id'])
        challan = get_object_or_404(Challan, challan_no=challan_no)
        weight = Weight.objects.get_or_create(challan=challan, material_id=material_id)[0]
        weight.weight_counts += "{},".format(weight_count)
        weight.save()
        # return JsonResponse({"weight": weight})
        return redirect(str(challan.get_update_url) + "?lmtid={}".format(material_id))
    else:
        return redirect("portal:home")


class ChallanRawCreateView(LoginRequiredMixin, CreateView):

    model = Challan
    template_name = "challans/raw_create.html"
    fields = ("party", )
    success_url = reverse_lazy("portal:home")

    def form_valid(self, form):
        challan = form.save()
        return redirect(reverse_lazy("challans:update", kwargs={"challan_no": challan.challan_no}))
