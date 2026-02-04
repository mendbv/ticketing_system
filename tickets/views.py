from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags 
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from .models import Ticket
from .forms import TicketCreateForm, TicketUpdateForm

User = get_user_model()

def send_html_email(subject, template_name, context, recipient_list):
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=None,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=True,
    )

@login_required
def client_dashboard(request):
    if not request.user.phone:
        messages.warning(request, "Please complete your profile contact details to continue.")
        return redirect('profile_confirmation')

    tickets = Ticket.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tickets/dashboard.html', {'tickets': tickets})

@login_required
def client_dashboard(request):
    tickets = Ticket.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tickets/dashboard.html', {'tickets': tickets})

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('client_dashboard')

    tickets = Ticket.objects.all()

    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=query) |
            Q(client__email__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query)
        )

    pending_tickets = tickets.filter(status='pending').order_by('created_at')
    processing_tickets = tickets.filter(status='processing').order_by('-updated_at')
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
    
    if ticket.status == 'pending':
        ticket.status = 'processing'
        ticket.save()

        # === EMAIL TO CLIENT (HTML) ===
        send_html_email(
            subject=f"Ticket Update #{ticket.ticket_number}",
            template_name='emails/status_update.html',
            context={
                'user_name': ticket.client.first_name,
                'ticket_number': ticket.ticket_number,
                'status': ticket.status,
                'status_display': ticket.get_status_display(),
                # request.build_absolute_uri строит полную ссылку (http://...)
                'dashboard_url': request.build_absolute_uri('/tickets/dashboard/')
            },
            recipient_list=[ticket.client.email]
        )
        
    return redirect('staff_dashboard')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.client = request.user
            ticket.save()

            # === EMAIL TO STAFF (HTML) ===
            staff_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
            
            if staff_emails:
                send_html_email(
                    subject=f"New Ticket: #{ticket.ticket_number}",
                    template_name='emails/new_ticket_staff.html',
                    context={
                        'ticket': ticket,
                        'staff_url': request.build_absolute_uri('/tickets/staff/')
                    },
                    recipient_list=list(staff_emails)
                )

            return redirect('client_dashboard')
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
def edit_ticket(request, pk):
    if not request.user.is_staff:
        return redirect('client_dashboard')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    old_status = ticket.status

    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save()
            
            # === EMAIL TO CLIENT (HTML) ===
            if old_status != updated_ticket.status:
                send_html_email(
                    subject=f"Ticket Update #{updated_ticket.ticket_number}",
                    template_name='emails/status_update.html',
                    context={
                        'user_name': updated_ticket.client.first_name,
                        'ticket_number': updated_ticket.ticket_number,
                        'status': updated_ticket.status,
                        'status_display': updated_ticket.get_status_display(),
                        'dashboard_url': request.build_absolute_uri('/tickets/dashboard/')
                    },
                    recipient_list=[updated_ticket.client.email]
                )

            return redirect('staff_dashboard')
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, 'tickets/edit_ticket.html', {'form': form, 'ticket': ticket})