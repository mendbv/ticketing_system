from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from .models import Ticket
from django import forms

# === ФОРМЫ (Можно вынести в forms.py, но для компактности здесь) ===

class ClientUploadForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['document_bundle']
        widgets = {
            'document_bundle': forms.FileInput(attrs={'class': 'file-input'}),
        }

class StaffTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'staff_internal_note', 'result_document']
        widgets = {
            'staff_internal_note': forms.Textarea(attrs={'rows': 3}),
        }

# === VIEWS ===

@login_required
def client_dashboard(request):
    if not request.user.phone:
        messages.warning(request, "Please complete your profile.")
        return redirect('profile_confirmation')

    tickets = Ticket.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tickets/dashboard.html', {'tickets': tickets})

@login_required
def client_upload_docs(request, pk):
    """Клиент загружает документы в оплаченный тикет"""
    ticket = get_object_or_404(Ticket, pk=pk, client=request.user)
    
    if request.method == 'POST':
        form = ClientUploadForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Documents uploaded successfully! We will review them shortly.")
            return redirect('client_dashboard')
    else:
        form = ClientUploadForm(instance=ticket)
    
    return render(request, 'tickets/upload_docs.html', {'form': form, 'ticket': ticket})

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('client_dashboard')

    tickets = Ticket.objects.all()
    
    # Поиск
    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=query) |
            Q(client__email__icontains=query) |
            Q(service_name__icontains=query)
        )

    # Фильтрация по статусам
    # paid = ждут документов от клиента
    waiting_docs = tickets.filter(status='paid').order_by('-created_at')
    # pending = документы есть, нужна проверка
    pending_tickets = tickets.filter(status='pending').order_by('created_at')
    # processing = в работе
    processing_tickets = tickets.filter(status='processing').order_by('-updated_at')
    # архив
    completed_tickets = tickets.filter(status__in=['ready', 'rejected']).order_by('-updated_at')

    context = {
        'waiting_docs': waiting_docs,
        'pending_tickets': pending_tickets,
        'processing_tickets': processing_tickets,
        'completed_tickets': completed_tickets,
        'search_query': query
    }
    return render(request, 'tickets/staff_dashboard.html', context)

@login_required
def edit_ticket(request, pk):
    """Персонал обрабатывает тикет"""
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    old_status = ticket.status

    if request.method == 'POST':
        form = StaffTicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save()
            
            # Если статус изменился, шлем уведомление
            if old_status != updated_ticket.status:
                # Тут можно раскомментировать отправку email
                pass 

            return redirect('staff_dashboard')
    else:
        form = StaffTicketForm(instance=ticket)
    return render(request, 'tickets/edit_ticket.html', {'form': form, 'ticket': ticket})

@login_required
@require_POST
def quick_move_to_processing(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.status == 'pending':
        ticket.status = 'processing'
        ticket.save()
    return redirect('staff_dashboard')