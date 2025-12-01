from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from django.contrib.auth.models import User

from .models import (
    PerformanceReviewCycle,
    PerformanceReview,
    PerformanceGoal,
    PerformanceEmailLog,
    AppreciationRecord,
)

EMAIL_FROM = 'noreply@emailintegration.com'


def _log_email(email_type, subject, recipients, status='sent', cycle=None, review=None, goal=None, error_message=''):
    PerformanceEmailLog.objects.create(
        email_type=email_type,
        subject=subject,
        recipient_list=', '.join(recipients),
        status=status,
        error_message=error_message,
        cycle=cycle,
        review=review,
        goal=goal,
    )


def _send_email(subject, template, context, recipients, email_type, cycle=None, review=None, goal=None, attachments=None):
    if not recipients:
        return
    html_message = render_to_string(template, context)
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=EMAIL_FROM,
        to=recipients,
    )
    email.content_subtype = 'html'
    attachments = attachments or []
    for attachment in attachments:
        if attachment:
            email.attach_file(attachment)

    try:
        email.send(fail_silently=False)
        _log_email(email_type, subject, recipients, cycle=cycle, review=review, goal=goal)
    except Exception as exc:
        _log_email(email_type, subject, recipients, status='failed', cycle=cycle, review=review, goal=goal, error_message=str(exc))


def _cycle_recipients(cycle):
    return [
        review.employee.email
        for review in cycle.reviews.select_related('employee')
        if review.employee.email
    ]


@shared_task
def launch_cycle_emails(cycle_id):
    """Send announcement, self-assessment link, and guidelines when a cycle is created."""
    try:
        cycle = PerformanceReviewCycle.objects.get(id=cycle_id)
    except PerformanceReviewCycle.DoesNotExist:
        return

    recipients = _cycle_recipients(cycle)
    context = {'cycle': cycle}

    if not cycle.announcement_sent:
        _send_email(
            subject=f"{cycle.name} Performance Review Kick-off",
            template='emails/performance/review_period_announcement.html',
            context=context,
            recipients=recipients,
            email_type='announcement',
            cycle=cycle,
        )
        cycle.announcement_sent = True

    if cycle.guidelines and not cycle.guidelines_sent:
        _send_email(
            subject=f"{cycle.name} Review Guidelines & Criteria",
            template='emails/performance/guidelines_email.html',
            context=context,
            recipients=recipients,
            email_type='guidelines',
            cycle=cycle,
        )
        cycle.guidelines_sent = True

    if cycle.self_assessment_link and not cycle.self_assessment_sent:
        _send_email(
            subject=f"{cycle.name} Self-Assessment Form",
            template='emails/performance/self_assessment_link.html',
            context=context,
            recipients=recipients,
            email_type='self_assessment',
            cycle=cycle,
        )
        cycle.self_assessment_sent = True

    cycle.save(update_fields=['announcement_sent', 'guidelines_sent', 'self_assessment_sent'])


@shared_task
def process_review_notifications():
    """Handle upcoming notifications, reminders, overdue alerts, and completion emails."""
    today = timezone.now().date()
    cycles = PerformanceReviewCycle.objects.all()

    for cycle in cycles:
        days_until_start = (cycle.start_date - today).days
        recipients = _cycle_recipients(cycle)
        context = {'cycle': cycle}

        if days_until_start == 14 and not cycle.upcoming_notification_sent:
            _send_email(
                subject=f"{cycle.name} Review Period Starts Soon",
                template='emails/performance/upcoming_review_notification.html',
                context=context,
                recipients=recipients,
                email_type='upcoming',
                cycle=cycle,
            )
            cycle.upcoming_notification_sent = True

        if today == cycle.submission_deadline and not cycle.self_assessment_sent and cycle.self_assessment_link:
            _send_email(
                subject=f"{cycle.name} Submission Deadline Today",
                template='emails/performance/submission_deadline_notice.html',
                context=context,
                recipients=recipients,
                email_type='self_assessment',
                cycle=cycle,
            )
            cycle.self_assessment_sent = True

        cycle.save(update_fields=['upcoming_notification_sent', 'self_assessment_sent'])

    reviews = PerformanceReview.objects.select_related('employee', 'manager', 'cycle')

    for review in reviews:
        employee_email = review.employee.email
        manager_email = review.manager.email if review.manager and review.manager.email else None
        recipients = [email for email in [employee_email] if email]
        reminder_context = {'review': review, 'cycle': review.cycle, 'manager': review.manager}

        if not review.self_assessment_submitted:
            days = review.days_until_deadline

            if days == 7 and not review.reminder_7_sent:
                _send_email(
                    subject='Performance Review Reminder: 7 Days Left',
                    template='emails/performance/reminder_7_days.html',
                    context=reminder_context,
                    recipients=recipients,
                    email_type='reminder_7',
                    review=review,
                )
                review.reminder_7_sent = True

            if days == 3 and not review.reminder_3_sent:
                _send_email(
                    subject='Performance Review Reminder: 3 Days Left',
                    template='emails/performance/reminder_3_days.html',
                    context=reminder_context,
                    recipients=recipients,
                    email_type='reminder_3',
                    review=review,
                )
                review.reminder_3_sent = True

            if days == 1 and not review.reminder_1_sent:
                _send_email(
                    subject='Urgent: Performance Review Due Tomorrow',
                    template='emails/performance/reminder_1_day.html',
                    context=reminder_context,
                    recipients=recipients,
                    email_type='reminder_1',
                    review=review,
                )
                review.reminder_1_sent = True

            if days < 0 and not review.overdue_notice_sent:
                _send_email(
                    subject='Performance Review Overdue',
                    template='emails/performance/overdue_notification.html',
                    context=reminder_context,
                    recipients=recipients,
                    email_type='overdue',
                    review=review,
                )
                review.overdue_notice_sent = True
                review.status = 'overdue'

        if review.meeting_scheduled_for and not review.meeting_confirmation_sent:
            meeting_recipients = [email for email in [employee_email, manager_email] if email]
            _send_email(
                subject='Performance Review Meeting Scheduled',
                template='emails/performance/meeting_confirmation.html',
                context=reminder_context,
                recipients=meeting_recipients,
                email_type='meeting_confirmation',
                review=review,
            )
            review.meeting_confirmation_sent = True
            review.status = 'meeting'

        if review.review_summary and not review.summary_shared:
            summary_recipients = [email for email in [employee_email, manager_email] if email]
            _send_email(
                subject='Performance Review Summary',
                template='emails/performance/review_summary.html',
                context=reminder_context,
                recipients=summary_recipients,
                email_type='review_summary',
                review=review,
            )
            review.summary_shared = True

        if review.goals_next_period and not review.goals_shared:
            goals_recipients = [email for email in [employee_email, manager_email] if email]
            _send_email(
                subject='Goals for Next Review Period',
                template='emails/performance/goal_setting_next_period.html',
                context=reminder_context,
                recipients=goals_recipients,
                email_type='goal_setting',
                review=review,
            )
            review.goals_shared = True

        review.save(
            update_fields=[
                'reminder_7_sent',
                'reminder_3_sent',
                'reminder_1_sent',
                'overdue_notice_sent',
                'status',
                'meeting_confirmation_sent',
                'summary_shared',
                'goals_shared',
            ]
        )


@shared_task
def process_goal_notifications():
    """Send goal achievement or course correction emails based on status."""
    goals = PerformanceGoal.objects.select_related('review', 'review__employee', 'review__manager', 'review__cycle')

    for goal in goals:
        review = goal.review
        employee_email = review.employee.email
        manager_email = review.manager.email if review.manager and review.manager.email else None
        recipients = [email for email in [employee_email, manager_email] if email]
        context = {'goal': goal, 'review': review}

        if goal.status == 'completed' and not goal.achievement_notified:
            _send_email(
                subject=f"Goal Achieved: {goal.title}",
                template='emails/performance/goal_achievement.html',
                context=context,
                recipients=recipients,
                email_type='goal_achievement',
                review=review,
                goal=goal,
            )
            goal.achievement_notified = True

        if goal.status == 'off_track' and not goal.course_correction_notified:
            _send_email(
                subject=f"Course Correction Needed: {goal.title}",
                template='emails/performance/course_correction.html',
                context=context,
                recipients=recipients,
                email_type='course_correction',
                review=review,
                goal=goal,
            )
            goal.course_correction_notified = True

        goal.save(update_fields=['achievement_notified', 'course_correction_notified'])


@shared_task
def send_quarterly_goal_reminders():
    """Quarterly nudge for teams to update goal progress."""
    now = timezone.now()
    reviews = PerformanceReview.objects.filter(status__in=['pending', 'submitted', 'review']).select_related(
        'employee', 'manager', 'cycle'
    )

    for review in reviews:
        recipients = [email for email in [review.employee.email, review.manager.email if review.manager else None] if email]
        context = {'review': review, 'cycle': review.cycle}
        _send_email(
            subject='Quarterly Goal Progress Reminder',
            template='emails/performance/goal_quarterly_reminder.html',
            context=context,
            recipients=recipients,
            email_type='goal_quarter',
            review=review,
        )
        review.last_quarterly_goal_reminder = now
        review.save(update_fields=['last_quarterly_goal_reminder'])


@shared_task
def send_appreciation_email_task(record_id):
    """Send appreciation email with optional badge attachment."""
    try:
        record = AppreciationRecord.objects.select_related('employee', 'manager').get(id=record_id)
    except AppreciationRecord.DoesNotExist:
        return

    recipients = [record.employee.email] if record.employee.email else []
    cc_recipients = []

    if record.cc_team:
        team_members = User.objects.filter(role_profile__manager=record.manager).exclude(id=record.employee_id)
        cc_recipients.extend([member.email for member in team_members if member.email])

    if record.cc_hr:
        hr_users = User.objects.filter(role_profile__role='hr')
        cc_recipients.extend([hr.email for hr in hr_users if hr.email])

    all_recipients = list(dict.fromkeys(recipients + cc_recipients))
    context = {'record': record, 'manager': record.manager}
    attachments = [record.badge_attachment.path] if record.badge_attachment else []

    _send_email(
        subject=record.subject,
        template='emails/performance/appreciation_email.html',
        context=context,
        recipients=all_recipients,
        email_type='appreciation',
    )

