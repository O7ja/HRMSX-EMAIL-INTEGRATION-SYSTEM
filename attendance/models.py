from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class AttendanceRecord(models.Model):
    """Daily attendance record for employees"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_date = models.DateField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.attendance_date}"
    
    class Meta:
        unique_together = ('employee', 'attendance_date')
        ordering = ['-attendance_date']
        verbose_name_plural = "Attendance Records"
    
    def is_late(self):
        """Check if check-in is after 9:00 AM"""
        if self.check_in_time:
            late_hour = self.check_in_time.hour == 9 and self.check_in_time.minute >= 30
            return self.check_in_time.hour > 9 or late_hour
        return False
    
    def is_missing_checkout(self):
        """Check if employee hasn't checked out"""
        return self.check_in_time and not self.check_out_time


class AttendanceEmailLog(models.Model):
    """Log for tracking sent attendance emails"""
    EMAIL_TYPE_CHOICES = [
        ('morning_reminder', 'Morning Check-in Reminder'),
        ('late_alert', 'Late Check-in Alert'),
        ('checkout_reminder', 'Missing Check-out Reminder'),
        ('weekly_report', 'Weekly Report'),
        ('monthly_report', 'Monthly Report'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_emails')
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPE_CHOICES)
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
    
    def __str__(self):
        return f"{self.employee.username} - {self.get_email_type_display()}"
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name_plural = "Attendance Email Logs"
