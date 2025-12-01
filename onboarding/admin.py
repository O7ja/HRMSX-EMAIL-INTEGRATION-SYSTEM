from django.contrib import admin
from .models import Onboarding, OnboardingChecklist, Offboarding, OffboardingChecklist, OnboardingEmailLog


class OnboardingChecklistInline(admin.TabularInline):
    model = OnboardingChecklist
    extra = 1


@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'status', 'welcome_email_sent']
    list_filter = ['status', 'start_date']
    search_fields = ['employee__username', 'employee__first_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OnboardingChecklistInline]


class OffboardingChecklistInline(admin.TabularInline):
    model = OffboardingChecklist
    extra = 1


@admin.register(Offboarding)
class OffboardingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'last_working_day', 'status', 'exit_email_sent']
    list_filter = ['status', 'last_working_day']
    search_fields = ['employee__username', 'employee__first_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OffboardingChecklistInline]


@admin.register(OnboardingEmailLog)
class OnboardingEmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'email_type', 'sent_at', 'status']
    list_filter = ['email_type', 'status', 'sent_at']
    search_fields = ['recipient_email']
    readonly_fields = ['sent_at']
