from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import UserRole, EmployeeProfile


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'users/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            try:
                # Redirect to dashboard based on role
                user_role = UserRole.objects.select_related('user').get(user=user)
                
                next_url = request.GET.get('next', None)
                
                if user_role.role == 'employee':
                    redirect_url = 'employee_dashboard'
                elif user_role.role == 'manager':
                    redirect_url = 'manager_dashboard'
                elif user_role.role == 'hr':
                    redirect_url = 'hr_dashboard'
                else:
                    messages.error(request, 'Invalid user role.')
                    logout(request)
                    return render(request, 'users/login.html')
                
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(redirect_url)
                    
            except UserRole.DoesNotExist:
                messages.error(request, 'User role not configured. Please contact admin.')
                logout(request)
                return render(request, 'users/login.html')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html')
    
    return render(request, 'users/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required(login_url='login')
def profile_view(request):
    """User profile view"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    employee_profile = None
    
    if hasattr(user, 'employee_profile'):
        employee_profile = user.employee_profile
    
    context = {
        'user': user,
        'role_profile': role_profile,
        'employee_profile': employee_profile,
    }
    
    return render(request, 'users/profile.html', context)


@login_required(login_url='login')
def edit_profile_view(request):
    """Edit user profile view"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        role_profile.phone = request.POST.get('phone', role_profile.phone)
        role_profile.department = request.POST.get('department', role_profile.department)
        role_profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    
    context = {
        'user': user,
        'role_profile': role_profile,
    }
    
    return render(request, 'users/edit_profile.html', context)


@login_required(login_url='login')
def employee_dashboard(request):
    """Employee dashboard view"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role != 'employee':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Get employee's attendance and leave data
    from attendance.models import AttendanceRecord
    from leave.models import LeaveRequest
    
    today = timezone.now().date()
    from datetime import timedelta
    
    # Get this month's attendance
    month_start = today.replace(day=1)
    attendance_records = AttendanceRecord.objects.filter(
        employee=user,
        attendance_date__gte=month_start
    ).order_by('-attendance_date')[:10]
    
    # Get pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        employee=user,
        status='pending'
    ).order_by('-created_at')[:5]
    
    # Get approved leaves
    approved_leaves = LeaveRequest.objects.filter(
        employee=user,
        status='approved'
    ).order_by('start_date')[:5]
    
    context = {
        'user': user,
        'role_profile': role_profile,
        'attendance_records': attendance_records,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
    }
    
    return render(request, 'dashboards/employee_dashboard.html', context)


@login_required(login_url='login')
def manager_dashboard(request):
    """Manager dashboard view"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role != 'manager':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Get subordinates
    subordinates = User.objects.filter(
        role_profile__manager=user,
        role_profile__role='employee'
    )
    
    from leave.models import LeaveRequest
    
    # Get pending leave requests from subordinates
    pending_leaves = LeaveRequest.objects.filter(
        employee__in=subordinates,
        status='pending'
    ).order_by('-created_at')
    
    context = {
        'user': user,
        'role_profile': role_profile,
        'subordinates': subordinates,
        'pending_leaves': pending_leaves,
    }
    
    return render(request, 'dashboards/manager_dashboard.html', context)


@login_required(login_url='login')
def hr_dashboard(request):
    """HR dashboard view"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role != 'hr':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Get all employees
    employees = User.objects.filter(role_profile__role='employee')
    
    from attendance.models import AttendanceRecord
    from leave.models import LeaveRequest
    
    today = timezone.now().date()
    
    # Get today's attendance summary
    today_attendance = AttendanceRecord.objects.filter(
        attendance_date=today
    )
    present_count = today_attendance.filter(status='present').count()
    late_count = today_attendance.filter(status='late').count()
    
    # Get all pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        status='pending'
    ).order_by('-created_at')
    
    context = {
        'user': user,
        'role_profile': role_profile,
        'total_employees': employees.count(),
        'today_attendance': today_attendance,
        'present_count': present_count,
        'late_count': late_count,
        'pending_leaves': pending_leaves,
    }
    
    return render(request, 'dashboards/hr_dashboard.html', context)
