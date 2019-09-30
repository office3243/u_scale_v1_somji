from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from challans.models import Challan
from .models import Payment, AccountTransaction, CashTransaction, WalletTransaction
from django.utils import timezone
import decimal
from bank_accounts.models import BankAccount


@login_required
def add(request, challan_no):

    challan = get_object_or_404(Challan, challan_no=challan_no)
    challan.save()
    party = challan.party
    wallet = party.get_wallet
    total_amount = challan.total_amount
    if request.method == "POST":
        print(request.POST)
        payment_mode = request.POST['payment_mode']
        payment = Payment.objects.get_or_create(challan=challan, payment_mode=payment_mode, amount=total_amount)[0]
        cash_amount = decimal.Decimal(request.POST.get('cash_amount' or 0))
        account_amount = decimal.Decimal(request.POST.get('account_amount') or 0)
        ac_less_amount = decimal.Decimal(request.POST.get('ac_less_amount') or 0)
        if cash_amount:
            cash_transaction = CashTransaction.objects.create(payment=payment, amount=cash_amount, payed_on=timezone.now(),
                                                              status="DN")
        if account_amount:
            bank_account_id = (request.POST.get('bank_account') or None)
            bank_account = get_object_or_404(BankAccount, id=bank_account_id, party=party)
            account_transaction = AccountTransaction.objects.create(payment=payment, amount=account_amount,
                                                                    bank_account=bank_account)
        if wallet is not None and ac_less_amount:
            wallet_transaction = WalletTransaction.objects.create(payment=payment, wallet=wallet,
                                                                  amount=ac_less_amount, is_full_amount=False)
        return redirect(challan.get_done_url)
    else:
        context = {"challan": challan}
        if wallet is not None:
            context['wallet'] = wallet
            context['wallet_payable_amount'], context['non_wallet_amount'] = wallet.get_payable_amount(total_amount)
            print(context)
        return render(request, "payments/add.html", context)
