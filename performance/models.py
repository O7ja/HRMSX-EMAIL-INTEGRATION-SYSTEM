from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PerformanceReviewCycle(models.Model):
    """Represents a company-wide performance review period."""

    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    submission_deadline = models.DateField()
    self_assessment_link = models.URLField(blank=True)
    guidelines = models.TextField(blank=True)
    criteria = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='review_cycles_created',
    )
    announcement_sent = models.BooleanField(default=False)
    upcoming_notification_sent = models.BooleanField(default=False)
    self_assessment_sent = models.BooleanField(default=False)
    guidelines_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Performance Review Cycle'
        verbose_name_plural = 'Performance Review Cycles'

    def __str__(self):
        return f"{self.name} ({self.start_date:%b %Y})"

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class PerformanceReview(models.Model):
    """Individual employee review linked to a cycle."""

    STATUS_CHOICES = [
        ('pending', 'Pending Self-Assessment'),
        ('submitted', 'Self-Assessment Submitted'),
        ('review', 'Manager Review In Progress'),
        ('meeting', 'Meeting Scheduled'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    cycle = models.ForeignKey(PerformanceReviewCycle, on_delete=models.CASCADE, related_name='reviews')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_reviews')
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_reviews',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submission_deadline = models.DateField()
    self_assessment_submitted = models.BooleanField(default=False)
    self_assessment_content = models.TextField(blank=True, help_text="Employee's self-assessment submission")
    self_assessment_submitted_at = models.DateTimeField(null=True, blank=True)
    manager_review_submitted_at = models.DateTimeField(null=True, blank=True)
    meeting_scheduled_for = models.DateTimeField(null=True, blank=True)
    meeting_confirmation_sent = models.BooleanField(default=False)
    review_summary = models.TextField(blank=True)
    summary_shared = models.BooleanField(default=False)
    goals_next_period = models.TextField(blank=True)
    goals_shared = models.BooleanField(default=False)
    reminder_7_sent = models.BooleanField(default=False)
    reminder_3_sent = models.BooleanField(default=False)
    reminder_1_sent = models.BooleanField(default=False)
    overdue_notice_sent = models.BooleanField(default=False)
    last_quarterly_goal_reminder = models.DateTimeField(null=True, blank=True)
    appreciation_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cycle', 'employee')
        ordering = ['employee__username']
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'

    def __str__(self):
        return f"{self.employee.get_full_name() or self.employee.username} - {self.cycle.name}"

    @property
    def days_until_deadline(self):
        return (self.submission_deadline - timezone.now().date()).days


class PerformanceGoal(models.Model):
    """Goals tracked within a review."""

    STATUS_CHOICES = [
        ('on_track', 'On Track'),
        ('off_track', 'Off Track'),
        ('completed', 'Completed'),
    ]

    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='on_track')
    progress_percent = models.PositiveSmallIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    course_correction_note = models.TextField(blank=True)
    achievement_notified = models.BooleanField(default=False)
    course_correction_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'title']
        verbose_name = 'Performance Goal'
        verbose_name_plural = 'Performance Goals'

    def __str__(self):
        return f"{self.title} ({self.review})"


class PerformanceEmailLog(models.Model):
    """Audit log for all performance related emails."""

    EMAIL_TYPE_CHOICES = [
        ('announcement', 'Review Period Announcement'),
        ('upcoming', 'Upcoming Review Notification'),
        ('self_assessment', 'Self-Assessment Link'),
        ('guidelines', 'Guidelines & Criteria'),
        ('reminder_7', '7 Day Reminder'),
        ('reminder_3', '3 Day Reminder'),
        ('reminder_1', '1 Day Reminder'),
        ('overdue', 'Overdue Notification'),
        ('meeting_confirmation', 'Meeting Confirmation'),
        ('review_summary', 'Review Summary'),
        ('goal_setting', 'Goal Setting'),
        ('appreciation', 'Appreciation Email'),
        ('goal_quarter', 'Quarterly Goal Reminder'),
        ('goal_achievement', 'Goal Achievement'),
        ('course_correction', 'Course Correction Suggestion'),
    ]

    cycle = models.ForeignKey(
        PerformanceReviewCycle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
    )
    review = models.ForeignKey(
        PerformanceReview,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
    )
    goal = models.ForeignKey(
        PerformanceGoal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
    )
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    recipient_list = models.TextField()
    status = models.CharField(max_length=20, default='sent')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Performance Email Log'
        verbose_name_plural = 'Performance Email Logs'

    def __str__(self):
        return f"{self.get_email_type_display()} - {self.recipient_list}"


class AppreciationRecord(models.Model):
    """Stores appreciation/recognition emails sent by managers."""

    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appreciations_sent',
    )
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appreciations_received',
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    cc_team = models.BooleanField(default=False)
    cc_hr = models.BooleanField(default=True)
    badge_attachment = models.FileField(upload_to='badges/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Appreciation Record'
        verbose_name_plural = 'Appreciation Records'

    def __str__(self):
        return f"{self.manager} -> {self.employee} ({self.created_at:%Y-%m-%d})"
