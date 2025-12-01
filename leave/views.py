from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import F
from .models import LeaveRequest, LeaveType, LeaveBalance
from .tasks import (
    send_leave_request_notification,
    send_leave_approval_notification,
    send_leave_rejection_notification
)
from users.models import UserRole


@login_required(login_url='login')
def request_leave(request):
    """Submit a leave request"""
    user = request.user
    leave_types = LeaveType.objects.filter(is_active=True)
    
    if request.method == 'POST':
        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id)
            
            # Create leave request
            leave_request = LeaveRequest.objects.create(
                employee=user,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='pending'
            )
            
            # Send notification to manager
            send_leave_request_notification.delay(leave_request.id)
            
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('leave_requests')
        except Exception as e:
            messages.error(request, f'Error submitting leave request: {str(e)}')
    
    context = {
        'leave_types': leave_types,
    }
    
    return render(request, 'leave/request_leave.html', context)


@login_required(login_url='login')
def leave_requests(request):
    """View leave requests"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role == 'employee':
        # Employee can view their own requests
        leave_requests = LeaveRequest.objects.filter(employee=user).order_by('-created_at')
    elif role_profile.role == 'manager':
        # Manager can view team members' requests from same department
        if role_profile.department:
            team_members = UserRole.objects.filter(
                department=role_profile.department,
                role='employee'
            ).values_list('user', flat=True)
            leave_requests = LeaveRequest.objects.filter(employee__in=team_members).order_by('-created_at')
        else:
            # If no department, no requests to show
            leave_requests = LeaveRequest.objects.none()
    elif role_profile.role == 'hr':
        # HR can view all requests
        leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    
    # Paginate
    paginator = Paginator(leave_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'is_pending': status_filter == 'pending',
        'is_approved': status_filter == 'approved',
        'is_rejected': status_filter == 'rejected',
    }
    
    return render(request, 'leave/requests.html', context)


@login_required(login_url='login')
def approve_leave(request, leave_id):
    """Approve a leave request"""
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    # Check authorization
    if role_profile.role == 'manager':
        # Check if employee is in manager's department
        if leave_request.employee.role_profile.department != role_profile.department:
            messages.error(request, 'You are not authorized to approve this request.')
            return redirect('leave_requests')
    elif role_profile.role != 'hr':
        messages.error(request, 'You are not authorized to approve leave requests.')
        return redirect('leave_requests')
    
    if request.method == 'POST':
        if leave_request.status == 'approved':
            messages.info(request, 'This leave request is already approved.')
            return redirect('leave_requests')

        leave_request.status = 'approved'
        leave_request.approved_by = user
        leave_request.save()

        # Update leave balance
        duration_days = leave_request.get_duration_days()
        employee_profile = getattr(leave_request.employee, 'employee_profile', None)
        default_total = employee_profile.leave_balance if employee_profile and employee_profile.leave_balance else 0

        balance, created = LeaveBalance.objects.get_or_create(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year,
            defaults={'total_balance': default_total, 'used_balance': 0}
        )
        LeaveBalance.objects.filter(id=balance.id).update(
            used_balance=F('used_balance') + duration_days
        )

        # Send approval notification
        send_leave_approval_notification.delay(leave_request.id)
        
        messages.success(request, 'Leave request approved.')
        return redirect('leave_requests')
    
    context = {
        'leave_request': leave_request,
    }
    
    return render(request, 'leave/approve_leave.html', context)


@login_required(login_url='login')
def reject_leave(request, leave_id):
    """Reject a leave request"""
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    # Check authorization
    if role_profile.role == 'manager':
        # Check if employee is in manager's department
        if leave_request.employee.role_profile.department != role_profile.department:
            messages.error(request, 'You are not authorized to reject this request.')
            return redirect('leave_requests')
    elif role_profile.role != 'hr':
        messages.error(request, 'You are not authorized to reject leave requests.')
        return redirect('leave_requests')
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        leave_request.status = 'rejected'
        leave_request.rejection_reason = rejection_reason
        leave_request.save()
        
        # Send rejection notification
        send_leave_rejection_notification.delay(leave_request.id)
        
        messages.success(request, 'Leave request rejected.')
        return redirect('leave_requests')
    
    context = {
        'leave_request': leave_request,
    }
    
    return render(request, 'leave/reject_leave.html', context)


@login_required(login_url='login')
def leave_calendar(request):
    """View team leave calendar"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role == 'employee':
        # Employee can see their own leaves
        leaves = LeaveRequest.objects.filter(
            employee=user,
            status='approved'
        )
    elif role_profile.role == 'manager':
        # Manager can see team leaves from same department
        if role_profile.department:
            team_members = UserRole.objects.filter(
                department=role_profile.department,
                role='employee'
            ).values_list('user', flat=True)
            leaves = LeaveRequest.objects.filter(
                employee__in=team_members,
                status='approved'
            )
        else:
            leaves = LeaveRequest.objects.none()
    elif role_profile.role == 'hr':
        # HR can see all leaves
        leaves = LeaveRequest.objects.filter(status='approved')
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    # Add duration calculation to each leave
    from datetime import timedelta
    leaves_with_duration = []
    for leave in leaves:
        duration = (leave.end_date - leave.start_date).days + 1  # +1 to include both start and end dates
        leave.duration = duration
        leaves_with_duration.append(leave)
    
    context = {
        'leaves': leaves_with_duration,
    }
    
    return render(request, 'leave/calendar.html', context)


@login_required(login_url='login')
def leave_balance(request):
    """View leave balance"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role != 'employee':
        messages.error(request, 'Only employees can view their leave balance.')
        return redirect('profile')
    
    from django.utils import timezone
    current_year = timezone.now().year
    
    balances = LeaveBalance.objects.filter(
        employee=user,
        year=current_year
    )
    
    context = {
        'balances': balances,
    }
    
    return render(request, 'leave/balance.html', context)
