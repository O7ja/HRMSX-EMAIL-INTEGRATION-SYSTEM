from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseForbidden

from users.models import UserRole
from .forms import PerformanceReviewCycleForm, AppreciationEmailForm, SelfAssessmentSubmissionForm
from .models import PerformanceReviewCycle, PerformanceReview
from .tasks import launch_cycle_emails, send_appreciation_email_task


def _get_user_role(user):
    try:
        return user.role_profile.role
    except UserRole.DoesNotExist:
        return None


@login_required(login_url='login')
def performance_dashboard(request):
    """Display cycles, reviews, and quick stats."""
    user_role = _get_user_role(request.user)
    if user_role not in ('hr', 'manager'):
        messages.error(request, 'You are not authorized to view the performance dashboard.')
        return redirect('profile')

    cycles = PerformanceReviewCycle.objects.select_related('created_by')
    today = timezone.now().date()
    if user_role == 'manager':
        reviews = PerformanceReview.objects.select_related('employee', 'cycle').filter(manager=request.user)
    else:
        reviews = PerformanceReview.objects.select_related('employee', 'cycle').all()

    stats = {
        'active_cycles': cycles.filter(start_date__lte=today, end_date__gte=today).count(),
        'pending_reviews': reviews.filter(status='pending').count(),
        'completed_reviews': reviews.filter(status='completed').count(),
        'overdue_reviews': reviews.filter(status='overdue').count(),
    }

    context = {
        'user_role': user_role,
        'cycles': cycles.order_by('-start_date')[:5],
        'reviews': reviews.order_by('employee__first_name')[:20],
        'stats': stats,
    }
    return render(request, 'performance/dashboard.html', context)


@login_required(login_url='login')
def create_review_cycle(request):
    """Allow HR to kick off a new review cycle."""
    user_role = _get_user_role(request.user)
    if user_role != 'hr':
        messages.error(request, 'Only HR can create review cycles.')
        return redirect('performance_dashboard')

    if request.method == 'POST':
        form = PerformanceReviewCycleForm(request.POST)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.created_by = request.user
            cycle.save()

            employees = User.objects.filter(role_profile__role='employee').select_related('role_profile')
            review_objects = []
            for employee in employees:
                role_profile = getattr(employee, 'role_profile', None)
                manager = role_profile.manager if role_profile else None
                review_objects.append(
                    PerformanceReview(
                        cycle=cycle,
                        employee=employee,
                        manager=manager,
                        submission_deadline=cycle.submission_deadline,
                    )
                )
            if review_objects:
                PerformanceReview.objects.bulk_create(review_objects, ignore_conflicts=True)

            launch_cycle_emails.delay(cycle.id)
            messages.success(request, 'Review cycle created and announcement emails queued.')
            return redirect('performance_dashboard')
    else:
        form = PerformanceReviewCycleForm()

    return render(request, 'performance/create_cycle.html', {'form': form})


@login_required(login_url='login')
def send_appreciation(request):
    """Allow managers/HR to send appreciation with optional badge attachment."""
    user_role = _get_user_role(request.user)
    if user_role not in ('manager', 'hr'):
        messages.error(request, 'Only managers and HR can send appreciation emails.')
        return redirect('performance_dashboard')

    if user_role == 'manager':
        team_members = User.objects.filter(role_profile__manager=request.user)
        has_members = team_members.exists()
        if not has_members:
            messages.info(request, 'No direct reports found to send appreciation.')
        employee_queryset = team_members if has_members else User.objects.none()
    else:
        employee_queryset = User.objects.filter(role_profile__role='employee')

    form = AppreciationEmailForm()
    form.fields['employee'].queryset = employee_queryset

    if request.method != 'POST':
        return render(request, 'performance/appreciation.html', {'form': form})

    form = AppreciationEmailForm(request.POST, request.FILES)
    form.fields['employee'].queryset = employee_queryset
    if form.is_valid():
        record = form.save(commit=False)
        record.manager = request.user
        record.save()
        send_appreciation_email_task.delay(record.id)
        messages.success(request, 'Appreciation email queued successfully.')
        return redirect('performance_dashboard')

    return render(request, 'performance/appreciation.html', {'form': form})


@login_required(login_url='login')
def employee_reviews(request):
    """Display pending reviews for the logged-in employee."""
    user_role = _get_user_role(request.user)
    if user_role != 'employee':
        messages.error(request, 'Only employees can view their reviews.')
        return redirect('profile')

    reviews = PerformanceReview.objects.filter(employee=request.user).select_related('cycle').order_by('-cycle__start_date')
    
    context = {
        'reviews': reviews,
        'pending_count': reviews.filter(status='pending').count(),
    }
    return render(request, 'performance/employee_reviews.html', context)


@login_required(login_url='login')
def submit_self_assessment(request, review_id):
    """Allow employee to submit their self-assessment."""
    review = get_object_or_404(PerformanceReview, id=review_id)
    
    # Check authorization
    if review.employee != request.user:
        return HttpResponseForbidden('You do not have permission to access this review.')
    
    # Check if already submitted
    if review.self_assessment_submitted:
        messages.info(request, 'Your self-assessment for this review has already been submitted.')
        return redirect('employee_reviews')
    
    if request.method == 'POST':
        form = SelfAssessmentSubmissionForm(request.POST)
        if form.is_valid():
            review.self_assessment_content = form.cleaned_data['assessment_content']
            review.self_assessment_submitted = True
            review.self_assessment_submitted_at = timezone.now()
            review.status = 'submitted'
            review.save()
            messages.success(request, 'Your self-assessment has been submitted successfully!')
            return redirect('employee_reviews')
    else:
        form = SelfAssessmentSubmissionForm()
    
    context = {
        'review': review,
        'cycle': review.cycle,
        'form': form,
    }
    return render(request, 'performance/submit_self_assessment.html', context)


@login_required(login_url='login')
def view_self_assessment(request, review_id):
    """View a submitted self-assessment (for manager/HR review)."""
    review = get_object_or_404(PerformanceReview, id=review_id)
    user_role = _get_user_role(request.user)
    
    # Check authorization - employee can view their own, manager/HR can view their reviews
    if request.user == review.employee:
        pass
    elif user_role == 'hr':
        pass
    elif user_role == 'manager' and review.manager == request.user:
        pass
    else:
        return HttpResponseForbidden('You do not have permission to access this review.')
    
    context = {
        'review': review,
        'cycle': review.cycle,
        'user_role': user_role,
    }
    return render(request, 'performance/view_self_assessment.html', context)
