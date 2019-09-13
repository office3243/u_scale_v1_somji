from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = "portal/home.html"


def temp_form_test(request):
    if request.POST:
        print(request.POST)
    return render(request, "portal/temp_form_test.html")
