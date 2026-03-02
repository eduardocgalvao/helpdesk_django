from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.db.models import Count, Q

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


    # Valida o formulário para vincular ao usuário logado
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
    def post(self, request, pk):
        ticket = get_object_or_404(Tickets, pk=pk)
        comment = request.POST.get('comment', '')
        
        # Salvar o comentário e marcar como completo
        ticket.comment = comment
        ticket.mark_has_complete()
        
        return redirect("tickets_list")


# Dashboard com métricas
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atual_user = self.request.user
        
        # Determinar se é admin/gestor ou colaborador
        is_admin = atual_user.is_superuser or atual_user.groups.filter(name__in=['Gestor', 'Admin']).exists()
        
        # Filtrar tickets baseado no tipo de usuário
        if is_admin:
            tickets = Tickets.objects.all()
        else:
            tickets = Tickets.objects.filter(usuario=atual_user)
        
        # Métricas
        total_tickets = tickets.count()
        open_tickets = tickets.filter(data_fechamento__isnull=True).count()
        closed_tickets = tickets.filter(data_fechamento__isnull=False).count()
        completion_rate = int((closed_tickets / total_tickets * 100)) if total_tickets > 0 else 0
        
        # Agrupar por status
        by_status = {
            'Aberto': open_tickets,
            'Concluído': closed_tickets
        }
        
        # Agrupar por prioridade
        priority_data = tickets.values('status__status_name').annotate(count=Count('id'))
        by_priority = {}
        for item in priority_data:
            status_name = item['status__status_name'] or 'Sem Prioridade'
            by_priority[status_name] = item['count']
        
        # Últimos 5 chamados
        recent_tickets = tickets.order_by('-data_abertura')[:5]
        
        context.update({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'closed_tickets': closed_tickets,
            'completion_rate': completion_rate,
            'by_status': by_status,
            'by_priority': by_priority,
            'recent_tickets': recent_tickets,
            'is_admin': is_admin
        })
        
        return context



