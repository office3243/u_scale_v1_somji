from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from challans.models import Challan
from .models import Payment, AccountTransaction, CashTransaction, WalletTransaction
from django.utils import timezone
import decimal
from bank_accounts.models import BankAccount
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def add(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no, is_entries_done=True)
    if challan.is_payed:
        messages.warning(request, "Challan is already paid")
        return redirect(challan.get_absolute_url)
    if not challan.is_rates_assigned:
        return redirect(challan.get_assign_rates_url)
    challan.save()
    party = challan.party
    wallet = party.get_wallet
    print(wallet)
    total_amount = challan.total_amount
    payment = Payment.objects.get_or_create(challan=challan)[0]
    payment.save()
    if request.method == "POST":
        print(request.POST)
        cash_amount = decimal.Decimal(request.POST.get('cash_amount') or 0)
        account_amount_1 = decimal.Decimal(request.POST.get('account_amount') or 0)
        account_amount_2 = decimal.Decimal(request.POST.get('account_amount_2') or 0)
        ac_less_amount = decimal.Decimal(request.POST.get('ac_less_amount') or 0)
        total_pay = cash_amount + account_amount_1 + account_amount_2 + ac_less_amount + payment.payed_amount
        if total_pay > payment.amount:
            messages.warning(request, "Amount should be less or equal to {}".format(payment.amount))
            return redirect(challan.get_payment_add_url)
        if cash_amount:
                cash_transaction = CashTransaction.objects.create(payment=payment, amount=cash_amount, payed_on=timezone.now(),
                                                              status="DN")
        if account_amount_1:
            bank_account_id_1 = (request.POST.get('bank_account') or None)
            bank_account_1 = get_object_or_404(BankAccount, id=bank_account_id_1, party=party)
            account_transaction_1 = AccountTransaction.objects.create(payment=payment, amount=account_amount_1,
                                                                      bank_account=bank_account_1)
        if wallet is not None and ac_less_amount:
            wallet_transaction = WalletTransaction.objects.create(payment=payment, wallet=wallet,
                                                                  amount=ac_less_amount)
        return redirect(challan.get_absolute_url)
    else:
        context = {"challan": challan, "payment": payment}
        if payment.payment_mode == "AL":
            context['wallet'] = wallet
            context['wallet_payable_amount'], context['non_wallet_amount'] = wallet.get_payable_amount(payment.get_remaining_amount)
            print(context)
        return render(request, "payments/add.html", context)


class PaymentListView(LoginRequiredMixin, ListView):

    template_name = "payments/list.html"
    model = Payment
    context_object_name = "payments"
    ordering = "-id"


class PaymentDetailView(LoginRequiredMixin, DetailView):

    template_name = "payments/detail.html"
    model = Payment
    context_object_name = "payment"
    slug_field = "id"
    slug_url_kwarg = "id"