from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, TemplateView
from payments.models import Payment, AccountTransaction, WalletTransaction, CashTransaction


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "cms_admin/dashboard.html"


class PaymentListView(LoginRequiredMixin, ListView):

    model = Payment
    template_name = "cms_admin/payments/list.html"
    context_object_name = "payments"
    ordering = "-id"
