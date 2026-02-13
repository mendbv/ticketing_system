from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Count
from django.core.mail import send_mail
from django import forms
from django.utils.translation import gettext as _

# Импорты моделей
from .models import Ticket, TicketFile, TicketLog
from services.models import Service  # <--- Импортируем модель Услуг

# Импорты утилит
from .utils import send_email_notification

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def log_history(ticket, user, action):
    TicketLog.objects.create(ticket=ticket, user=user, action=action)

# === CLIENT VIEWS ===

@login_required
def client_dashboard(request):
    if not request.user.phone:
        messages.warning(request, _("Please complete your profile details."))
        return redirect('profile_confirmation')

    tickets = Ticket.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tickets/dashboard.html', {'tickets': tickets})

@login_required
def client_upload_docs(request, pk):
    """
    Страница загрузки документов клиентом.
    Теперь показывает список требований из оригинальной услуги.
    """
    ticket = get_object_or_404(Ticket, pk=pk, client=request.user)
    
    # 1. Ищем услугу по имени, чтобы показать требования
    # (Мы ищем по точному совпадению имени, которое сохранили в тикете)
    service_obj = Service.objects.filter(name=ticket.service_name).first()
    requirements = []
    
    if service_obj and service_obj.documents_required:
        # Разбиваем текст на строки и убираем пустые/пробельные строки
        raw_lines = service_obj.documents_required.split('\n')
        requirements = [line.strip() for line in raw_lines if line.strip()]
    
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        
        if files:
            for f in files:
                TicketFile.objects.create(ticket=ticket, file=f)
            
            # Если статус был "Оплачено", меняем на "Проверка"
            if ticket.status == 'paid':
                ticket.status = 'pending'
                ticket.save()
            
            # Пишем в лог
            log_history(ticket, request.user, f"Uploaded {len(files)} document(s)")
            
            messages.success(request, _("Documents uploaded successfully."))
            return redirect('client_dashboard')
        else:
            messages.error(request, _("Please select at least one file."))

    return render(request, 'tickets/upload_docs.html', {
        'ticket': ticket,
        'requirements': requirements
    })

# === STAFF VIEWS ===

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('client_dashboard')

    status_filter = request.GET.get('status', 'all')
    query = request.GET.get('q', '')

    tickets = Ticket.objects.all().order_by('-created_at')

    if status_filter != 'all':
        tickets = tickets.filter(status=status_filter)
    
    if query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=query) |
            Q(client__email__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query)
        )

    # Статистика для меню
    counts = Ticket.objects.values('status').annotate(total=Count('status'))
    stats = {item['status']: item['total'] for item in counts}
    total_count = Ticket.objects.count()

    context = {
        'tickets': tickets,
        'stats': stats,
        'total_count': total_count,
        'current_status': status_filter,
        'search_query': query
    }
    return render(request, 'tickets/staff_dashboard.html', context)

@login_required
def edit_ticket(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        internal_note = request.POST.get('staff_internal_note')
        result_file = request.FILES.get('result_document')

        # Смена статуса
        if new_status and new_status != ticket.status:
            # Лог
            log_history(ticket, request.user, f"Changed status: {ticket.status} -> {new_status}")
            
            # Уведомление клиента по Email
            send_email_notification(
                subject=f"Update on Ticket #{ticket.ticket_number}",
                template_name='emails/status_change.html',
                context={
                    'ticket': ticket,
                    'dashboard_url': request.build_absolute_uri('/tickets/dashboard/')
                },
                recipients=[ticket.client.email]
            )
            
            ticket.status = new_status
        
        # Обновление заметки
        if internal_note and internal_note != ticket.staff_internal_note:
            log_history(ticket, request.user, "Updated internal note")
            ticket.staff_internal_note = internal_note
            
        # Загрузка результата
        if result_file:
            ticket.result_document = result_file
            log_history(ticket, request.user, "Uploaded result document")
            if ticket.status == 'processing':
                ticket.status = 'ready'
                log_history(ticket, request.user, "Auto-changed status to Ready")

        ticket.save()
        messages.success(request, _("Ticket updated."))
        return redirect('edit_ticket', pk=ticket.pk)

    return render(request, 'tickets/staff_ticket_detail.html', {'ticket': ticket})

@login_required
@require_POST
def staff_assign_ticket(request, pk):
    """
    Назначение или снятие ответственного сотрудника.
    """
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    action = request.POST.get('action')

    if action == 'take':
        ticket.assigned_to = request.user
        log_history(ticket, request.user, "Assigned ticket to self")
        messages.success(request, _("You are now responsible for this ticket."))
        
    elif action == 'release':
        ticket.assigned_to = None
        log_history(ticket, request.user, "Unassigned ticket")
        messages.info(request, _("Ticket unassigned."))
        
    ticket.save()
    return redirect('edit_ticket', pk=ticket.pk)

@login_required
@require_POST
def quick_move_to_processing(request, pk):
    """
    Быстрая кнопка из списка (если еще используется).
    """
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.status in ['paid', 'pending']:
        ticket.status = 'processing'
        ticket.save()
        log_history(ticket, request.user, "Quick process start")
        
    return redirect('staff_dashboard')