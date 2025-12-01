from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Onboarding, Offboarding, OnboardingChecklist, OffboardingChecklist
from .tasks import send_welcome_email, send_exit_process_email, send_farewell_email
from users.models import UserRole, EmployeeProfile


@login_required(login_url='login')
def onboarding_status(request):
    """View onboarding status"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role == 'employee':
        # employee view their own onboarding
        onboarding = get_object_or_404(Onboarding, employee=user)
    elif role_profile.role == 'hr':
        # hr can view all onboardings
        onboarding_id = request.GET.get('id')
        if onboarding_id:
            onboarding = get_object_or_404(Onboarding, id=onboarding_id)
        else:
            onboardings = Onboarding.objects.all().order_by('-start_date')
            context = {'onboardings': onboardings}
            return render(request, 'onboarding/list.html', context)
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    checklist_items = onboarding.checklist_items.all().order_by('day')
    
    context = {
        'onboarding': onboarding,
        'checklist_items': checklist_items,
    }
    
    return render(request, 'onboarding/status.html', context)


@login_required(login_url='login')
def update_checklist_item(request, item_id):
    """Update checklist item completion status"""
    user = request.user
    checklist_item = get_object_or_404(OnboardingChecklist, id=item_id)
    
    # checking auth
    if checklist_item.onboarding.employee != user:
        role_profile = get_object_or_404(UserRole, user=user)
        if role_profile.role != 'hr':
            messages.error(request, 'You are not authorized to update this item.')
            return redirect('onboarding_status')
    
    if request.method == 'POST':
        is_completed = request.POST.get('is_completed') == 'on'
        
        if is_completed:
            from django.utils import timezone
            checklist_item.is_completed = True
            checklist_item.completed_at = timezone.now()
        else:
            checklist_item.is_completed = False
            checklist_item.completed_at = None
        
        checklist_item.save()
        messages.success(request, 'Checklist item updated.')
    
    return redirect('onboarding_status')


@login_required(login_url='login')
def offboarding_status(request):
    """View offboarding status"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role == 'employee':
        
        offboarding = Offboarding.objects.filter(employee=user).first()
        if not offboarding:
            messages.error(request, 'No offboarding record found.')
            return redirect('profile')
    elif role_profile.role == 'hr':
        
        offboarding_id = request.GET.get('id')
        if offboarding_id:
            offboarding = get_object_or_404(Offboarding, id=offboarding_id)
        else:
            offboardings = Offboarding.objects.all().order_by('-last_working_day')
            context = {'offboardings': offboardings}
            return render(request, 'onboarding/offboarding_list.html', context)
    else:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('profile')
    
    checklist_items = offboarding.checklist_items.all()
    
    context = {
        'offboarding': offboarding,
        'checklist_items': checklist_items,
    }
    
    return render(request, 'onboarding/offboarding_status.html', context)


@login_required(login_url='login')
def update_offboarding_checklist_item(request, item_id):
    """Update offboarding checklist item completion status"""
    user = request.user
    checklist_item = get_object_or_404(OffboardingChecklist, id=item_id)
    
    # Check authorization
    if checklist_item.offboarding.employee != user:
        role_profile = get_object_or_404(UserRole, user=user)
        if role_profile.role != 'hr':
            messages.error(request, 'You are not authorized to update this item.')
            return redirect('offboarding_status')
    
    if request.method == 'POST':
        is_completed = request.POST.get('is_completed') == 'on'
        
        if is_completed:
            from django.utils import timezone
            checklist_item.is_completed = True
            checklist_item.completed_at = timezone.now()
        else:
            checklist_item.is_completed = False
            checklist_item.completed_at = None
        
        checklist_item.save()
        messages.success(request, 'Checklist item updated.')
    
    return redirect('offboarding_status')


@login_required(login_url='login')
def new_employee_onboarding(request):
    """Create onboarding for a new employee (HR only)"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role != 'hr':
        messages.error(request, 'Only HR can create onboarding records.')
        return redirect('profile')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id') or request.POST.get('employee')
        try:
            employee = User.objects.get(id=employee_id)
            
            # Create onboarding record
            onboarding, created = Onboarding.objects.get_or_create(employee=employee)
            
            
            checklist_tasks = [
                ('Complete IT setup (laptop, email, access)', 3),
                ('Meet with HR for policies and benefits overview', 3),
                ('IT systems and tools training', 5),
                ('Department introduction and team lunch', 5),
                ('First week review with manager', 7),
                ('Initial project assignment', 7),
            ]
            
            for task, day in checklist_tasks:
                OnboardingChecklist.objects.get_or_create(
                    onboarding=onboarding,
                    task=task,
                    day=day
                )
            
            # Send welcome email
            send_welcome_email.delay(employee.id)
            
            messages.success(request, 'Onboarding record created and welcome email sent.')
            return redirect('onboarding_status')
        except User.DoesNotExist:
            messages.error(request, 'Employee not found.')
    
    employees = User.objects.filter(role_profile__role='employee').distinct()
    
    context = {
        'employees': employees,
    }
    
    return render(request, 'onboarding/new_employee.html', context)


@login_required(login_url='login')
def initiate_offboarding(request, employee_id):
    """Initiate offboarding for an employee (HR only)"""
    user = request.user
    role_profile = get_object_or_404(UserRole, user=user)
    
    if role_profile.role != 'hr':
        messages.error(request, 'Only HR can initiate offboarding.')
        return redirect('profile')
    
    employee = get_object_or_404(User, id=employee_id)
    
    if request.method == 'POST':
        last_working_day = request.POST.get('last_working_day')
        final_settlement = request.POST.get('final_settlement', '')
        
        try:
            offboarding, created = Offboarding.objects.get_or_create(
                employee=employee,
                defaults={
                    'last_working_day': last_working_day,
                    'final_settlement': final_settlement,
                }
            )
            
            # Create default offboarding checklist
            offboarding_tasks = [
                'Return laptop and equipment',
                'Revoke system access',
                'Clear outstanding dues',
                'Document handover',
                'Collect signed exit form',
            ]
            
            for task in offboarding_tasks:
                OffboardingChecklist.objects.get_or_create(
                    offboarding=offboarding,
                    task=task
                )
            
            # Send exit process email
            send_exit_process_email.delay(offboarding.id)
            
            messages.success(request, 'Offboarding initiated and exit process email sent.')
            return redirect('offboarding_status')
        except Exception as e:
            messages.error(request, f'Error initiating offboarding: {str(e)}')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'onboarding/initiate_offboarding.html', context)
