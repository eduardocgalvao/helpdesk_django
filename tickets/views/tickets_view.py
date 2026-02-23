from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group

from ..models import Tickets

# View dos chamados
class TicketListView(LoginRequiredMixin, ListView):
    model = Tickets
    template_name = 'tickets/tickets_list.html'
    context_object_name = 'tickets'
    
    # Lista somente os chamados do usuário logado 
    def get_queryset(self):
        atual_user = self.request.user

        # Se for "Admin" ou "Gestor", vai ter um acesso mais aberto ao gerenciamento dos chamados
        if atual_user.is_superuser or atual_user.groups.filter(name__in=['Gestor', 'Admin']).exists():
            return Tickets.objects.all().order_by('-id')
        
        # Colaborador só tem acesso somente aos seus próprios chamados
        return Tickets.objects.filter(usuario=atual_user).order_by('-id')

# Criar  chamados
class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Tickets
    fields = ["equipamento", "description", "data_fechamento", "status"]
    success_url = reverse_lazy('tickets_list')
    
    def form_valid(self, form):

        form.instance.usuario = self.request.user
        return super().form_valid(form)
    
    
# Atualizar chamados
class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Tickets
    fields = ["equipamento", "description", "data_fechamento", "status"]
    success_url = reverse_lazy('tickets_list')

# Deletar chamados
class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Tickets
    template_name = 'tickets/tickets_confirm_delete.html'
    success_url = reverse_lazy('tickets_list')


class HomeView(TemplateView):
    template_name = "home.html"

# Marcar chamado como concluído
class TicketCompleteView(View):
    def get(self, request, pk):
        ticket = get_object_or_404(Tickets, pk=pk)
        ticket.mark_has_complete()
        return redirect("tickets_list")



