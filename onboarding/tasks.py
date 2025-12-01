from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta, date
from .models import Onboarding, Offboarding, OnboardingEmailLog
from django.contrib.auth.models import User


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new employee"""
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            return
        
        # Create temporary password (in production, use proper password reset link)
        temp_password = User.objects.make_random_password(length=12)
        
        subject = "Welcome to Our Company!"
        context = {
            'employee_name': user.get_full_name() or user.username,
            'username': user.username,
            'temp_password': temp_password,
            'first_day_info': 'Please report at 9:00 AM on your first day.',
        }
        
        html_message = render_to_string('emails/welcome.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[user.email],
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)
        
        # Update onboarding status
        onboarding = Onboarding.objects.filter(employee=user).first()
        if onboarding:
            onboarding.welcome_email_sent = True
            onboarding.save()
        
        OnboardingEmailLog.objects.create(
            recipient_email=user.email,
            email_type='welcome',
            status='sent'
        )
    except Exception as e:
        print(f"Error sending welcome email: {e}")


@shared_task
def send_day_3_checklist():
    """Send day 3 checklist email"""
    three_days_ago = date.today() - timedelta(days=3)
    
    # Get onboarding records where start_date was 3 days ago
    onboardings = Onboarding.objects.filter(
        start_date=three_days_ago,
        day_3_checklist_sent=False,
        status='in_progress'
    )
    
    for onboarding in onboardings:
        employee = onboarding.employee
        
        if not employee.email:
            continue
        
        subject = "Day 3 Onboarding Checklist"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'checklist_items': onboarding.checklist_items.filter(day=3),
        }
        
        html_message = render_to_string('emails/day3_checklist.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            
            onboarding.day_3_checklist_sent = True
            onboarding.save()
            
            OnboardingEmailLog.objects.create(
                recipient_email=employee.email,
                email_type='day_3',
                status='sent'
            )
        except Exception as e:
            print(f"Error sending day 3 checklist: {e}")


@shared_task
def send_day_5_checklist():
    """Send day 5 checklist email"""
    five_days_ago = date.today() - timedelta(days=5)
    
    # Get onboarding records where start_date was 5 days ago
    onboardings = Onboarding.objects.filter(
        start_date=five_days_ago,
        day_5_checklist_sent=False,
        status='in_progress'
    )
    
    for onboarding in onboardings:
        employee = onboarding.employee
        
        if not employee.email:
            continue
        
        subject = "Day 5 Onboarding Checklist"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'checklist_items': onboarding.checklist_items.filter(day=5),
        }
        
        html_message = render_to_string('emails/day5_checklist.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            
            onboarding.day_5_checklist_sent = True
            onboarding.save()
            
            OnboardingEmailLog.objects.create(
                recipient_email=employee.email,
                email_type='day_5',
                status='sent'
            )
        except Exception as e:
            print(f"Error sending day 5 checklist: {e}")


@shared_task
def send_day_7_checklist():
    """Send day 7 checklist email"""
    seven_days_ago = date.today() - timedelta(days=7)
    
    # Get onboarding records where start_date was 7 days ago
    onboardings = Onboarding.objects.filter(
        start_date=seven_days_ago,
        day_7_checklist_sent=False,
        status='in_progress'
    )
    
    for onboarding in onboardings:
        employee = onboarding.employee
        
        if not employee.email:
            continue
        
        subject = "Day 7 Onboarding Checklist"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'checklist_items': onboarding.checklist_items.filter(day=7),
        }
        
        html_message = render_to_string('emails/day7_checklist.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        try:
            email.send(fail_silently=False)
            
            onboarding.day_7_checklist_sent = True
            onboarding.save()
            
            OnboardingEmailLog.objects.create(
                recipient_email=employee.email,
                email_type='day_7',
                status='sent'
            )
        except Exception as e:
            print(f"Error sending day 7 checklist: {e}")


@shared_task
def send_exit_process_email(offboarding_id):
    """Send exit process email to departing employee"""
    try:
        offboarding = Offboarding.objects.get(id=offboarding_id)
        employee = offboarding.employee
        
        if not employee.email:
            return
        
        subject = "Exit Process Information"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'last_working_day': offboarding.last_working_day,
            'checklist_items': offboarding.checklist_items.all(),
        }
        
        html_message = render_to_string('emails/exit_process.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)
        
        offboarding.exit_email_sent = True
        offboarding.save()
        
        OnboardingEmailLog.objects.create(
            recipient_email=employee.email,
            email_type='exit_process',
            status='sent'
        )
    except Exception as e:
        print(f"Error sending exit process email: {e}")


@shared_task
def send_farewell_email(offboarding_id):
    """Send farewell email to departing employee"""
    try:
        offboarding = Offboarding.objects.get(id=offboarding_id)
        employee = offboarding.employee
        
        if not employee.email:
            return
        
        subject = "Farewell - Best Wishes for Your Future!"
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'last_working_day': offboarding.last_working_day,
        }
        
        html_message = render_to_string('emails/farewell.html', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email='noreply@emailintegration.com',
            to=[employee.email],
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)
        
        offboarding.farewell_email_sent = True
        offboarding.save()
        
        OnboardingEmailLog.objects.create(
            recipient_email=employee.email,
            email_type='farewell',
            status='sent'
        )
    except Exception as e:
        print(f"Error sending farewell email: {e}")
