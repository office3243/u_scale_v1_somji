from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, FormView
from .models import Material


class MaterialListView(LoginRequiredMixin, ListView):

    model = Material
    template_name = "materials/list.html"
    context_object_name = "materials"

