from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse_lazy
from .models import Party
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class PartyListView(LoginRequiredMixin, ListView):
    model = Party
    context_object_name = "parties"
    template_name = "parties/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class PartyAddView(LoginRequiredMixin, CreateView):

    model = Party
    fields = ("name", "rate_type", "rate_group", "party_code", "address", "phone", "whatsapp", "email", "is_wallet_party", "extra_info")
    template_name = "parties/add.html"
    success_url = reverse_lazy('parties:list')

    def form_valid(self, form):
        party = form.save()
        messages.success(self.request, "Party Created Successfully {}".format(party.party_code))
        return super().form_valid(form)


class PartyDetailView(LoginRequiredMixin, DetailView):
    model = Party
    template_name = "parties/detail.html"
    slug_field = "party_code"
    slug_url_kwarg = "party_code"

    def get_object(self, queryset=None):
        party = super().get_object()
        if party.is_active:
            return party
        return Http404("Party Is Not Active")
