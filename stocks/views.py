from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.generic import DeleteView, CreateView, UpdateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MaterialStock
from django.utils import timezone
import datetime


class DateStockDetailView(LoginRequiredMixin, TemplateView):

    template_name = "stocks/date_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        stock_date = timezone.datetime(day=int(self.kwargs['day']), month=int(self.kwargs['month']), year=int(self.kwargs['year'])).date()
        stocks = get_list_or_404(MaterialStock, date=stock_date)
        for stock in stocks:
            stock.save()
        context['stocks'] = stocks
        context['date'] = stock_date
        context['previous_date'] = stock_date - timezone.timedelta(days=1)
        context['next_date'] = stock_date + timezone.timedelta(days=1)
        return context


class StockView(LoginRequiredMixin, TemplateView):

    template_name = "stocks/view.html"


class DateStockListView(LoginRequiredMixin, TemplateView):

    template_name = "stocks/date_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['dates'] = set(MaterialStock.objects.values_list("date", flat=True))
        return context
