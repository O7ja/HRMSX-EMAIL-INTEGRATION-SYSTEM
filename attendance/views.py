from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from .models import AttendanceRecord
from users.models import UserRole
import json


@login_required(login_url='login')
def check_in(request):
    """Employee check-in"""
    user = request.user
    today = date.today()
    
    # Check if already checked in
    attendance = AttendanceRecord.objects.filter(
        employee=user,
        attendance_date=today
    ).first()
    
    if request.method == 'POST':
        if attendance and attendance.check_in_time:
            messages.warning(request, 'You have already checked in today.')
        else:
            now = timezone.now()
            
            if not attendance:
                attendance = AttendanceRecord.objects.create(
                    employee=user,
                    attendance_date=today,
                    check_in_time=now
                )
            else:
                attendance.check_in_time = now
                attendance.save()
            
            # Determine status
            if now.hour > 9 or (now.hour == 9 and now.minute >= 30):
                attendance.status = 'late'
            else:
                attendance.status = 'present'
            attendance.save()
            
            messages.success(request, f'Check-in recorded at {now.strftime("%H:%M:%S")}')
            return redirect('employee_dashboard')
    
    context = {
        'attendance': attendance,
    }
    
    return render(request, 'attendance/check_in.html', context)


@login_required(login_url='login')
def check_out(request):
    """Employee check-out"""
    user = request.user
    today = date.today()
    
    # Get today's attendance
    attendance = AttendanceRecord.objects.filter(
        employee=user,
        attendance_date=today
    ).first()
    
    if request.method == 'POST':
        if not attendance or not attendance.check_in_time:
            messages.error(request, 'Please check in first.')
        elif attendance.check_out_time:
            messages.warning(request, 'You have already checked out today.')
        else:
            now = timezone.now()
            attendance.check_out_time = now
            attendance.save()
            
            messages.success(request, f'Check-out recorded at {now.strftime("%H:%M:%S")}')
            return redirect('employee_dashboard')
    
    context = {
        'attendance': attendance,
    }
    
    return render(request, 'attendance/check_out.html', context)


@login_required(login_url='login')
def attendance_report(request):
    """View attendance report"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role == 'employee':
        # Employee can only view their own attendance
        records = AttendanceRecord.objects.filter(employee=user).order_by('-attendance_date')
    elif role_profile.role == 'manager':
        # Manager can view their own attendance and their team members
        # Get all employees in the same department
        if role_profile.department:
            team_members = UserRole.objects.filter(
                department=role_profile.department,
                role='employee'
            ).values_list('user', flat=True)
            # Include manager's own records
            records = AttendanceRecord.objects.filter(
                employee__in=list(team_members) + [user]
            ).order_by('-attendance_date')
        else:
            # If no department, just show manager's own records
            records = AttendanceRecord.objects.filter(employee=user).order_by('-attendance_date')
    elif role_profile.role == 'hr':
        # HR can view all attendance
        records = AttendanceRecord.objects.all().order_by('-attendance_date')
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Filter by date range if provided
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if from_date:
        records = records.filter(attendance_date__gte=from_date)
    if to_date:
        records = records.filter(attendance_date__lte=to_date)
    
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'attendance/report.html', context)


@login_required(login_url='login')
def attendance_summary(request):
    """View attendance summary statistics"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    if role_profile.role == 'employee':
        # Employee summary
        month_records = AttendanceRecord.objects.filter(
            employee=user,
            attendance_date__gte=month_start
        )
        year_records = AttendanceRecord.objects.filter(
            employee=user,
            attendance_date__gte=year_start
        )
    elif role_profile.role == 'manager':
        # Manager summary - show team members from same department
        if role_profile.department:
            team_members = UserRole.objects.filter(
                department=role_profile.department,
                role='employee'
            ).values_list('user', flat=True)
            month_records = AttendanceRecord.objects.filter(
                employee__in=team_members,
                attendance_date__gte=month_start
            )
            year_records = AttendanceRecord.objects.filter(
                employee__in=team_members,
                attendance_date__gte=year_start
            )
        else:
            month_records = AttendanceRecord.objects.none()
            year_records = AttendanceRecord.objects.none()
    elif role_profile.role == 'hr':
        # HR summary
        month_records = AttendanceRecord.objects.filter(attendance_date__gte=month_start)
        year_records = AttendanceRecord.objects.filter(attendance_date__gte=year_start)
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Calculate statistics
    month_stats = {
        'total': month_records.count(),
        'present': month_records.filter(status='present').count(),
        'late': month_records.filter(status='late').count(),
        'absent': month_records.filter(status='absent').count(),
        'half_day': month_records.filter(status='half_day').count(),
    }
    
    year_stats = {
        'total': year_records.count(),
        'present': year_records.filter(status='present').count(),
        'late': year_records.filter(status='late').count(),
        'absent': year_records.filter(status='absent').count(),
        'half_day': year_records.filter(status='half_day').count(),
    }
    
    context = {
        'month_stats': month_stats,
        'year_stats': year_stats,
    }
    
    return render(request, 'attendance/summary.html', context)
