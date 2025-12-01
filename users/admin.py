from django.contrib import admin
from .models import UserRole, EmployeeProfile


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'phone', 'manager']
    list_filter = ['role', 'department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'date_of_joining', 'leave_balance', 'is_active_employee']
    list_filter = ['date_of_joining', 'is_active_employee', 'created_at']
    search_fields = ['employee_id', 'user__username', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at']
