from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy

from ..models import Tickets


class TicketListView(ListView):
    model = Tickets


class TicketCreateView(CreateView):
    model = Tickets
    fields = ["equipamento", "description", "data_fechamento", "status"]

    

class TicketUpdateView(UpdateView):
    model = Tickets
    fields = ["equipamento", "description", "data_fechamento", "status"]


class TicketDeleteView(DeleteView):
    model = Tickets


class HomeView(TemplateView):
    template_name = "home.html"



