from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.request_leave, name='request_leave'),
    path('requests/', views.leave_requests, name='leave_requests'),
    path('approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('calendar/', views.leave_calendar, name='leave_calendar'),
    path('balance/', views.leave_balance, name='leave_balance'),
]
