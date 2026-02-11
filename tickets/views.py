from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Count
from django.core.mail import send_mail
from .models import Ticket, TicketFile
from django import forms

# === CLIENT VIEWS ===

@login_required
def client_dashboard(request):
    if not request.user.phone:
        messages.warning(request, "Please complete your profile.")
        return redirect('profile_confirmation')
    tickets = Ticket.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tickets/dashboard.html', {'tickets': tickets})

@login_required
def client_upload_docs(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, client=request.user)
    
    if request.method == 'POST':
        # Получаем список файлов из input name="files"
        files = request.FILES.getlist('files')
        
        if files:
            for f in files:
                TicketFile.objects.create(ticket=ticket, file=f)
            
            # Меняем статус
            if ticket.status == 'paid':
                ticket.status = 'pending'
                ticket.save()
            
            messages.success(request, f"{len(files)} document(s) uploaded successfully.")
            return redirect('client_dashboard')
        else:
            messages.error(request, "Please select at least one file.")

    return render(request, 'tickets/upload_docs.html', {'ticket': ticket})

# === STAFF VIEWS (REFACTORED) ===

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('client_dashboard')

    # Получаем параметр фильтрации из URL (по умолчанию 'all')
    status_filter = request.GET.get('status', 'all')
    query = request.GET.get('q', '')

    tickets = Ticket.objects.all().order_by('-created_at')

    # Фильтрация
    if status_filter != 'all':
        tickets = tickets.filter(status=status_filter)
    
    # Поиск
    if query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=query) |
            Q(client__email__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query)
        )

    # Считаем количество для табов
    counts = Ticket.objects.values('status').annotate(total=Count('status'))
    # Преобразуем в словарь { 'paid': 5, 'pending': 2 ... }
    stats = {item['status']: item['total'] for item in counts}
    
    total_count = Ticket.objects.count()

    context = {
        'tickets': tickets,
        'stats': stats,
        'total_count': total_count,
        'current_status': status_filter,
        'search_query': query
    }
    return render(request, 'tickets/staff_dashboard_v2.html', context)

@login_required
def edit_ticket(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        # Обновление статуса и заметок
        new_status = request.POST.get('status')
        internal_note = request.POST.get('staff_internal_note')
        result_file = request.FILES.get('result_document')

        if new_status:
            ticket.status = new_status
        
        if internal_note:
            ticket.staff_internal_note = internal_note
            
        if result_file:
            ticket.result_document = result_file
            if new_status == 'processing':
                ticket.status = 'ready' # Автоматически ставим Ready если загрузили результат

        ticket.save()
        messages.success(request, "Ticket updated.")
        return redirect('edit_ticket', pk=ticket.pk)

    return render(request, 'tickets/staff_ticket_detail.html', {'ticket': ticket})

@login_required
@require_POST
def quick_move_to_processing(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    # Если статус paid или pending -> переводим в processing
    if ticket.status in ['paid', 'pending']:
        ticket.status = 'processing'
        ticket.save()
    return redirect('staff_dashboard')