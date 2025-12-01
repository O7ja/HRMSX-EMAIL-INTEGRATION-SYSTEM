from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date, timedelta
from .models import AttendanceRecord, AttendanceEmailLog
from users.models import UserRole, EmployeeProfile


@shared_task
def send_morning_checkin_reminder():
    """Send morning reminder at 9:00 AM to employees who haven't checked in"""
    today = date.today()
    
    # fet all active employees
    employees = User.objects.filter(role_profile__role='employee')
    
    for employee in employees:
        # check if employee has checked in today
        has_checkin = AttendanceRecord.objects.filter(
            employee=employee,
            attendance_date=today,
            check_in_time__isnull=False
        ).exists()
        
        if not has_checkin:
            send_checkin_reminder_email(employee)


@shared_task
def send_late_checkin_alert():
    """Send late check-in alert at 9:30 AM"""
    today = date.today()
    
    # get all late check in
    late_checkins = AttendanceRecord.objects.filter(
        attendance_date=today,
        check_in_time__isnull=False
    ).exclude(check_in_time__hour=8)  
    
    for record in late_checkins:
        if record.is_late():
            send_late_checkin_email(record)

  # get all employees with check-in but no checkouts
@shared_task
def send_missing_checkout_reminder():
    """Send missing check-out reminder at 6:00 PM"""
    today = date.today()
    
  
    missing_checkouts = AttendanceRecord.objects.filter(
        attendance_date=today,
        check_in_time__isnull=False,
        check_out_time__isnull=True
    )
    
    for record in missing_checkouts:
        send_checkout_reminder_email(record)


@shared_task
def send_weekly_attendance_report():
    """Send weekly attendance report on Monday at 8:00 AM"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # get all managers
    managers = User.objects.filter(role_profile__role='manager')
    
    for manager in managers:
        # get subordinates
        subordinates = User.objects.filter(
            role_profile__manager=manager,
            role_profile__role='employee'
        )
        
        # get attendance records for the week
        attendance_records = AttendanceRecord.objects.filter(
            employee__in=subordinates,
            attendance_date__gte=week_start,
            attendance_date__lte=week_end
        ).order_by('-attendance_date')
        
        if manager.email and attendance_records.exists():
            send_weekly_report_email(manager, attendance_records, week_start, week_end)


@shared_task
def send_monthly_attendance_report():
    """Send monthly attendance report on 1st of month at 9:00 AM"""
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    # get month end
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    # get all HR users
    hr_users = User.objects.filter(role_profile__role='hr')
    
    for hr_user in hr_users:
        # get all employees
        employees = User.objects.filter(role_profile__role='employee')
        
        # get attendance records for the month
        attendance_records = AttendanceRecord.objects.filter(
            employee__in=employees,
            attendance_date__gte=month_start,
            attendance_date__lte=month_end
        ).order_by('-attendance_date')
        
        if hr_user.email and attendance_records.exists():
            send_monthly_report_email(hr_user, attendance_records, month_start, month_end)


# Helper functions for sending emails

def send_checkin_reminder_email(employee):
    """Send check-in reminder to employee"""
    subject = "Morning Check-in Reminder"
    context = {
        'employee_name': employee.get_full_name() or employee.username,
    }
    
    html_message = render_to_string('emails/checkin_reminder.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='noreply@emailintegration.com',
        to=[employee.email],
    )
    email.content_subtype = 'html'
    
    try:
        email.send(fail_silently=False)
        
        # Log the email
        AttendanceEmailLog.objects.create(
            employee=employee,
            email_type='morning_reminder',
            recipient_email=employee.email,
            status='sent'
        )
    except Exception as e:
        AttendanceEmailLog.objects.create(
            employee=employee,
            email_type='morning_reminder',
            recipient_email=employee.email,
            status='failed'
        )


def send_late_checkin_email(record):
    """Send late check-in alert to employee and manager"""
    employee = record.employee
    manager = employee.role_profile.manager
    
    subject = f"Late Check-in Alert - {record.attendance_date}"
    context = {
        'employee_name': employee.get_full_name() or employee.username,
        'check_in_time': record.check_in_time,
    }
    
    html_message = render_to_string('emails/late_checkin_alert.html', context)
    
    recipients = [employee.email]
    if manager and manager.email:
        recipients.append(manager.email)
    
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='noreply@emailintegration.com',
        to=recipients,
    )
    email.content_subtype = 'html'
    
    try:
        email.send(fail_silently=False)
        
        # Log the email
        AttendanceEmailLog.objects.create(
            employee=employee,
            email_type='late_alert',
            recipient_email=','.join(recipients),
            status='sent'
        )
    except Exception as e:
        AttendanceEmailLog.objects.create(
            employee=employee,
            email_type='late_alert',
            recipient_email=','.join(recipients),
            status='failed'
        )


def send_checkout_reminder_email(record):
    """Send check-out reminder to employee"""
    employee = record.employee
    
    subject = "Missing Check-out Reminder"
    context = {
        'employee_name': employee.get_full_name() or employee.username,
        'check_in_time': record.check_in_time,
    }
    
    html_message = render_to_string('emails/checkout_reminder.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='noreply@emailintegration.com',
        to=[employee.email],
    )
    email.content_subtype = 'html'
    
    try:
        email.send(fail_silently=False)
        
        AttendanceEmailLog.objects.create(
            employee=employee,
            email_type='checkout_reminder',
            recipient_email=employee.email,
            status='sent'
        )
    except Exception as e:
        AttendanceEmailLog.objects.create(
            employee=employee,
            email_type='checkout_reminder',
            recipient_email=employee.email,
            status='failed'
        )


def send_weekly_report_email(manager, records, week_start, week_end):
    """Send weekly attendance report to manager"""
    subject = f"Weekly Attendance Report - {week_start} to {week_end}"
    context = {
        'manager_name': manager.get_full_name() or manager.username,
        'records': records,
        'week_start': week_start,
        'week_end': week_end,
    }
    
    html_message = render_to_string('emails/weekly_report.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='noreply@emailintegration.com',
        to=[manager.email],
    )
    email.content_subtype = 'html'
    
    try:
        email.send(fail_silently=False)
        
        AttendanceEmailLog.objects.create(
            employee=manager,
            email_type='weekly_report',
            recipient_email=manager.email,
            status='sent'
        )
    except Exception as e:
        AttendanceEmailLog.objects.create(
            employee=manager,
            email_type='weekly_report',
            recipient_email=manager.email,
            status='failed'
        )


def send_monthly_report_email(hr_user, records, month_start, month_end):
    """Send monthly attendance report to HR"""
    subject = f"Monthly Attendance Report - {month_start.strftime('%B %Y')}"
    
    # Calculate statistics
    total_records = records.count()
    present_count = records.filter(status='present').count()
    late_count = records.filter(status='late').count()
    absent_count = records.filter(status='absent').count()
    
    context = {
        'hr_name': hr_user.get_full_name() or hr_user.username,
        'records': records,
        'month_start': month_start,
        'month_end': month_end,
        'total_records': total_records,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
    }
    
    html_message = render_to_string('emails/monthly_report.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email='noreply@emailintegration.com',
        to=[hr_user.email],
    )
    email.content_subtype = 'html'
    
    try:
        email.send(fail_silently=False)
        
        AttendanceEmailLog.objects.create(
            employee=hr_user,
            email_type='monthly_report',
            recipient_email=hr_user.email,
            status='sent'
        )
    except Exception as e:
        AttendanceEmailLog.objects.create(
            employee=hr_user,
            email_type='monthly_report',
            recipient_email=hr_user.email,
            status='failed'
        )
