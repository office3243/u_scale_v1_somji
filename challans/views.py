from django.shortcuts import render, get_object_or_404, redirect
from .models import Challan, Weight, WeightEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, DetailView
from django.urls import reverse_lazy
from materials.models import Material
from parties.models import Party
from django.http import JsonResponse
from .forms import ChallanRawCreateForm, WeightForm
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages


@login_required
def challan_entries(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    if request.method == "POST":
        pass
    else:
        materials = Material.objects.filter(is_active=True)
        parties = Party.objects.filter(is_active=True)
        context = {'materials': materials, "parties": parties, "challan": challan}
        return render(request, "challans/entries.html", context)


@login_required
def entries_done(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    challan.is_entry_done = True
    challan.save()
    return redirect("challans:assign_rates", {"challan_no": challan.challan_no})


@login_required
def assign_rates(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    WeightFormSet = inlineformset_factory(Challan, Weight, form=WeightForm, extra=0, can_delete=False)
    if request.method == "POST":
        formset = WeightFormSet(request.POST, instance=challan)
        if formset.is_valid():
            formset.save()
            return redirect(challan.get_payment_add_url)
    formset = WeightFormSet(instance=challan)
    context = {"challan": challan, "formset": formset}
    return render(request, "challans/assign_rates.html", context)


def weight_entry_create(request):

    """
    Weight instance will be get_or_created by passing material_id and challan_id .
    A new instance of WeightEntry model will be created with relation to above Weight instance.
    And material_id will be passed to request param named 'lmtid'
    """
    if request.method == "POST":
        entry = float(request.POST['entry_weight'])
        challan = get_object_or_404(Challan, challan_no=request.POST['challan_no'])
        material_id = request.POST['material_id']
        """dont allow entry less than 0.1"""
        if entry > 0.1:
            print(request.POST)
            material = get_object_or_404(Material, id=material_id)
            weight = Weight.objects.get_or_create(challan=challan, material=material)[0]
            weight_entry = WeightEntry.objects.create(weight=weight, entry=entry)
            try:
                """for fields validation"""
                weight_entry.full_clean()
            except Exception as e:
                messages.warning(request, e)
                weight_entry.delete()
        else:
            messages.warning(request, "Entry Cannot be less than 0.1")
        return redirect(str(challan.get_entries_url) + "?lmtid={}".format(material_id))
    else:
        return redirect("portal:home")


class ChallanCreateView(LoginRequiredMixin, CreateView):

    model = Challan
    template_name = "challans/create.html"
    fields = ("party", )
    success_url = reverse_lazy("portal:home")

    def form_valid(self, form):
        challan = form.save()
        return redirect(challan.get_entries_url)


@login_required
def challan_publish(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    if request.method == "POST":
        print(request.POST, request.FILES)
        gateway_choice = request.POST['gateway_choice']
        is_payed = request.POST['is_payed']
        extra_info = request.POST['extra_info']
        image = request.FILES['image']
        challan.payment_gateway_choice = gateway_choice
        challan.is_payed = is_payed
        challan.image = image
        challan.extra_info = extra_info
        challan.save()
        return redirect("portal:home")
    else:
        materials = Material.objects.filter(is_active=True)
        parties = Party.objects.filter(is_active=True)
        context = {'materials': materials, "parties": parties, "challan": challan}
        return render(request, "challans/update.html", context)


class ChallanDoneView(LoginRequiredMixin, DetailView):

    model = Challan
    slug_url_kwarg = "challan_no"
    slug_field = "challan_no"
    template_name = "challans/done.html"
