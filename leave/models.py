from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class LeaveType(models.Model):
    """Leave types: Sick, Vacation, Personal, etc."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Leave Types"


class LeaveRequest(models.Model):
    """Leave request submitted by employees"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")
        if self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Leave Requests"
    
    def get_duration_days(self):
        """Calculate leave duration in days"""
        return (self.end_date - self.start_date).days + 1


class LeaveBalance(models.Model):
    """Track employee leave balance"""
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    total_balance = models.IntegerField(default=0)
    used_balance = models.IntegerField(default=0)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name} ({self.year})"
    
    @property
    def available_balance(self):
        return self.total_balance - self.used_balance
    
    class Meta:
        unique_together = ('employee', 'leave_type', 'year')
        verbose_name_plural = "Leave Balances"


class LeaveEmailLog(models.Model):
    """Log for tracking sent leave emails"""
    EMAIL_TYPE_CHOICES = [
        ('request_submitted', 'Leave Request Submitted'),
        ('approved', 'Leave Approved'),
        ('rejected', 'Leave Rejected'),
        ('reminder_before', 'Reminder Before Leave'),
        ('reminder_after', 'Reminder After Leave'),
    ]
    
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='email_logs')
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPE_CHOICES)
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
    
    def __str__(self):
        return f"{self.leave_request.employee.username} - {self.get_email_type_display()}"
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name_plural = "Leave Email Logs"
