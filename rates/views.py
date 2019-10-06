from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse_lazy
from .models import RateGroup, GroupMaterialRate
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class RatesView(LoginRequiredMixin, TemplateView):
    template_name = "rates/rates_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['rate_groups'] = RateGroup.objects.filter(is_active=True)
        return context


class RateGroupListView(LoginRequiredMixin, ListView):
    model = RateGroup
    context_object_name = "rate_groups"
    template_name = "rates/rate_groups/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class RateGroupDetailView(LoginRequiredMixin, DetailView):
    model = RateGroup
    template_name = "rates/rate_groups/detail.html"
    slug_field = "id"
    slug_url_kwarg = "id"
    context_object_name = "rate_group"
    # def get_object(self, queryset=None):
    #     party = super().get_object()
    #     if party.is_active:
    #         return party
    #     return Http404("Rate Group Is Not Active")
