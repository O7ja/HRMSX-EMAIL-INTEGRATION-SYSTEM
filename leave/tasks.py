from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import LeaveRequest, LeaveEmailLog
from users.models import UserRole


@shared_task
def send_leave_request_notification(leave_request_id):
    """Send email when a leave request is submitted"""
    try:
        leave_request = LeaveRequest.objects.get(id=leave_request_id)
        employee = leave_request.employee
        manager = employee.role_profile.manager
        
        if not manager or not manager.email:
            return
        
        subject = f"New Leave Request from {employee.get_full_name()}"
        context = {
            'manager_name': manager.get_full_name() or manager.username,
            'employee_name': employee.get_full_name() or employee.username,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'reason': leave_request.reason,
            'duration': leave_request.get_duration_days(),
        }
        
        html_message = render_to_string('emails/leave_request_submitted.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[manager.email],
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)
        
        LeaveEmailLog.objects.create(
            leave_request=leave_request,
            email_type='request_submitted',
            recipient_email=manager.email,
            status='sent'
        )
    except Exception as e:
        print(f"Error sending leave request notification: {e}")


@shared_task
def send_leave_approval_notification(leave_request_id):
    """Send email when a leave request is approved"""
    try:
        print(f"\n{'='*60}")
        print(f"SENDING LEAVE APPROVAL EMAIL FOR REQUEST ID: {leave_request_id}")
        print(f"{'='*60}\n")
        
        leave_request = LeaveRequest.objects.get(id=leave_request_id)
        employee = leave_request.employee
        
        if not employee.email:
            print(f"ERROR: Employee {employee.username} has no email address!")
            return
        
        subject = "Your Leave Request Has Been Approved"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'approved_by': leave_request.approved_by.get_full_name() if leave_request.approved_by else 'HR',
        }
        
        print(f"Context: {context}")
        
        html_message = render_to_string('emails/leave_approved.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)
        print(f"EMAIL SENT SUCCESSFULLY TO: {employee.email}")
        
        LeaveEmailLog.objects.create(
            leave_request=leave_request,
            email_type='approved',
            recipient_email=employee.email,
            status='sent'
        )
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"ERROR sending leave approval notification: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")


@shared_task
def send_leave_rejection_notification(leave_request_id):
    """Send email when a leave request is rejected"""
    try:
        leave_request = LeaveRequest.objects.get(id=leave_request_id)
        employee = leave_request.employee
        
        if not employee.email:
            return
        
        subject = "Your Leave Request Has Been Rejected"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'rejection_reason': leave_request.rejection_reason,
        }
        
        html_message = render_to_string('emails/leave_rejected.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)
        
        LeaveEmailLog.objects.create(
            leave_request=leave_request,
            email_type='rejected',
            recipient_email=employee.email,
            status='sent'
        )
    except Exception as e:
        print(f"Error sending leave rejection notification: {e}")


@shared_task
def send_leave_reminder_before():
    """Send reminder email 1 day before leave starts"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # get all approved leaves starting tomorrow
    upcoming_leaves = LeaveRequest.objects.filter(
        status='approved',
        start_date=tomorrow
    )
    
    for leave_request in upcoming_leaves:
        employee = leave_request.employee
        
        if not employee.email:
            continue
        
        subject = "Leave Starts Tomorrow"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
        }
        
        html_message = render_to_string('emails/leave_reminder_before.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            
            LeaveEmailLog.objects.create(
                leave_request=leave_request,
                email_type='reminder_before',
                recipient_email=employee.email,
                status='sent'
            )
        except Exception as e:
            print(f"Error sending leave reminder: {e}")


@shared_task
def send_leave_reminder_after():
    """Send reminder email after leave ends"""
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # get all approved leaves that ended yesterday
    completed_leaves = LeaveRequest.objects.filter(
        status='approved',
        end_date=yesterday
    )
    
    for leave_request in completed_leaves:
        employee = leave_request.employee
        manager = employee.role_profile.manager
        
        if not employee.email:
            continue
        
        subject = "Welcome Back!"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'leave_type': leave_request.leave_type.name,
        }
        
        html_message = render_to_string('emails/leave_reminder_after.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            
            LeaveEmailLog.objects.create(
                leave_request=leave_request,
                email_type='reminder_after',
                recipient_email=employee.email,
                status='sent'
            )
        except Exception as e:
            print(f"Error sending leave after reminder: {e}")
