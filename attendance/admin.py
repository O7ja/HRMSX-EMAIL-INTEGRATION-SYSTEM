from django.contrib import admin
from .models import AttendanceRecord, AttendanceEmailLog


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance_date', 'check_in_time', 'check_out_time', 'status']
    list_filter = ['status', 'attendance_date', 'created_at']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'attendance_date'


@admin.register(AttendanceEmailLog)
class AttendanceEmailLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'email_type', 'recipient_email', 'sent_at', 'status']
    list_filter = ['email_type', 'status', 'sent_at']
    search_fields = ['employee__username', 'recipient_email']
    readonly_fields = ['sent_at']
