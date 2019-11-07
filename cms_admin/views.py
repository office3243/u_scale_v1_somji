from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, TemplateView
from payments.models import Payment, AccountTransaction, WalletTransaction, CashTransaction
from django.urls import reverse_lazy
from parties.models import Wallet, WalletAdvance


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "cms_admin/dashboard.html"


class PaymentListView(LoginRequiredMixin, ListView):

    model = Payment
    template_name = "cms_admin/payments/list.html"
    context_object_name = "payments"
    ordering = "-id"


class PaymentDetailView(LoginRequiredMixin, DetailView):

    template_name = "cms_admin/payments/detail.html"
    model = Payment
    context_object_name = "payment"
    slug_field = "id"
    slug_url_kwarg = "id"


class AccountTransactionListView(LoginRequiredMixin, ListView):

    model = AccountTransaction
    template_name = "cms_admin/payments/account_transactions/list.html"
    context_object_name = "account_transactions"
    ordering = "-id"


class AccountTransactionDetailView(LoginRequiredMixin, DetailView):

    model = AccountTransaction
    context_object_name = "account_transaction"
    template_name = "cms_admin/payments/account_transactions/detail.html"
    slug_field = "id"
    slug_url_kwarg = "id"


class AccountTransactionUpdateView(LoginRequiredMixin, UpdateView):

    model = AccountTransaction
    context_object_name = "account_transaction"
    template_name = "cms_admin/payments/account_transactions/update.html"
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy("cms_admin:account_transactions_list")
    fields = ("payment_party", "payed_on", "status")


class WalletListView(LoginRequiredMixin, ListView):

    model = Wallet
    context_object_name = "wallets"
    template_name = "cms_admin/wallets/list.html"
    ordering = "-id"


class WalletAdvanceListView(LoginRequiredMixin, ListView):
    model = WalletAdvance
    context_object_name = "wallet_advances"
    template_name = "cms_admin/wallets/wallet_advances/list.html"
    ordering = "-id"

