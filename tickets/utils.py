import os
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from weasyprint import HTML

def send_email_notification(subject, template_name, context, recipients):
    """
    Универсальная функция отправки красивых HTML-писем.
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=None, # Использует DEFAULT_FROM_EMAIL из settings
        recipient_list=recipients,
        html_message=html_message,
        fail_silently=True
    )

def generate_invoice_pdf(ticket):
    """
    Генерирует PDF инвойс и сохраняет его в поле invoice тикета.
    """
    # Рендерим HTML для инвойса
    html_string = render_to_string('invoices/invoice_pdf.html', {'ticket': ticket})
    
    # Создаем PDF байты
    pdf_file = HTML(string=html_string).write_pdf()
    
    # Формируем имя файла
    filename = f"Invoice_{ticket.ticket_number}.pdf"
    
    # Сохраняем файл в модель
    # save=True автоматически обновит запись в базе данных
    ticket.invoice.save(filename, ContentFile(pdf_file), save=True)
    
    return ticket.invoice.url