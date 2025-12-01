from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Onboarding(models.Model):
    """Onboarding process for new employees"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    employee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding')
    start_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    welcome_email_sent = models.BooleanField(default=False)
    day_3_checklist_sent = models.BooleanField(default=False)
    day_5_checklist_sent = models.BooleanField(default=False)
    day_7_checklist_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Onboarding - {self.employee.get_full_name()}"
    
    class Meta:
        verbose_name_plural = "Onboarding Records"


class OnboardingChecklist(models.Model):
    """Tasks for onboarding checklist"""
    onboarding = models.ForeignKey(Onboarding, on_delete=models.CASCADE, related_name='checklist_items')
    task = models.CharField(max_length=200)
    day = models.IntegerField(help_text="Day number (3, 5, 7, etc.)")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.task} - Day {self.day}"
    
    class Meta:
        ordering = ['day']
        verbose_name_plural = "Onboarding Checklists"


class Offboarding(models.Model):
    """Offboarding process for departing employees"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    employee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='offboarding')
    last_working_day = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    exit_email_sent = models.BooleanField(default=False)
    farewell_email_sent = models.BooleanField(default=False)
    final_settlement = models.TextField(blank=True, help_text="Final settlement details")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Offboarding - {self.employee.get_full_name()}"
    
    class Meta:
        verbose_name_plural = "Offboarding Records"


class OffboardingChecklist(models.Model):
    """Tasks for offboarding checklist"""
    offboarding = models.ForeignKey(Offboarding, on_delete=models.CASCADE, related_name='checklist_items')
    task = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.task}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Offboarding Checklists"


class OnboardingEmailLog(models.Model):
    """Log for tracking sent onboarding emails"""
    EMAIL_TYPE_CHOICES = [
        ('welcome', 'Welcome Email'),
        ('day_3', 'Day 3 Checklist'),
        ('day_5', 'Day 5 Checklist'),
        ('day_7', 'Day 7 Checklist'),
        ('exit_process', 'Exit Process'),
        ('farewell', 'Farewell Email'),
    ]
    
    recipient_email = models.EmailField()
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPE_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
    
    def __str__(self):
        return f"{self.recipient_email} - {self.get_email_type_display()}"
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name_plural = "Onboarding Email Logs"
