from django.contrib import admin

from .models import (
    PerformanceReviewCycle,
    PerformanceReview,
    PerformanceGoal,
    PerformanceEmailLog,
    AppreciationRecord,
)


@admin.register(PerformanceReviewCycle)
class PerformanceReviewCycleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'submission_deadline', 'created_by')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = (
        'cycle',
        'employee',
        'manager',
        'status',
        'submission_deadline',
        'meeting_scheduled_for',
    )
    list_filter = ('status', 'submission_deadline', 'cycle')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    autocomplete_fields = ('cycle', 'employee', 'manager')


@admin.register(PerformanceGoal)
class PerformanceGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'review', 'status', 'progress_percent', 'due_date')
    list_filter = ('status',)
    search_fields = ('title',)
    autocomplete_fields = ('review',)


@admin.register(PerformanceEmailLog)
class PerformanceEmailLogAdmin(admin.ModelAdmin):
    list_display = ('email_type', 'subject', 'sent_at', 'status')
    list_filter = ('email_type', 'status')
    search_fields = ('subject', 'recipient_list')
    readonly_fields = ('sent_at',)


@admin.register(AppreciationRecord)
class AppreciationRecordAdmin(admin.ModelAdmin):
    list_display = ('manager', 'employee', 'subject', 'created_at')
    list_filter = ('manager', 'employee')
    search_fields = ('subject', 'message')
    autocomplete_fields = ('manager', 'employee')
