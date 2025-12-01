from django.contrib import admin
from .models import LeaveType, LeaveRequest, LeaveBalance, LeaveEmailLog


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by']
    list_filter = ['status', 'leave_type', 'created_at', 'start_date']
    search_fields = ['employee__username', 'employee__first_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'total_balance', 'used_balance', 'available_balance']
    list_filter = ['leave_type', 'year', 'created_at']
    search_fields = ['employee__username']


@admin.register(LeaveEmailLog)
class LeaveEmailLogAdmin(admin.ModelAdmin):
    list_display = ['leave_request', 'email_type', 'recipient_email', 'sent_at', 'status']
    list_filter = ['email_type', 'status', 'sent_at']
    search_fields = ['recipient_email', 'leave_request__employee__username']
    readonly_fields = ['sent_at']
