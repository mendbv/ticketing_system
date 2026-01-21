from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Ticket
from .forms import TicketCreateForm, TicketUpdateForm

@login_required
def client_dashboard(request):
    tickets = Ticket.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tickets/dashboard.html', {'tickets': tickets})

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('client_dashboard')

    # Базовый QuerySet
    tickets = Ticket.objects.all()

    # 1. Поиск (по номеру тикета, имени, фамилии или email клиента)
    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=query) |
            Q(client__email__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query)
        )

    # 2. Разделение по статусам
    # Pending: сортируем от старых к новым (чтобы не забыть старые)
    pending_tickets = tickets.filter(status='pending').order_by('created_at')
    
    # Processing: сортируем по дате обновления
    processing_tickets = tickets.filter(status='processing').order_by('-updated_at')
    
    # Completed (Ready + Rejected): архивные
    completed_tickets = tickets.filter(status__in=['ready', 'rejected']).order_by('-updated_at')

    context = {
        'pending_tickets': pending_tickets,
        'processing_tickets': processing_tickets,
        'completed_tickets': completed_tickets,
        'search_query': query
    }
    return render(request, 'tickets/staff_dashboard.html', context)

@login_required
@require_POST
def quick_move_to_processing(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Меняем статус только если он сейчас Pending
    if ticket.status == 'pending':
        ticket.status = 'processing'
        ticket.save()
        
    return redirect('staff_dashboard')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.client = request.user
            ticket.save()
            return redirect('client_dashboard')
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
def edit_ticket(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, 'tickets/edit_ticket.html', {'form': form, 'ticket': ticket})