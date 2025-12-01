from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.performance_dashboard, name='performance_dashboard'),
    path('cycles/new/', views.create_review_cycle, name='create_review_cycle'),
    path('appreciation/', views.send_appreciation, name='send_appreciation'),
    path('my-reviews/', views.employee_reviews, name='employee_reviews'),
    path('reviews/<int:review_id>/self-assessment/submit/', views.submit_self_assessment, name='submit_self_assessment'),
    path('reviews/<int:review_id>/self-assessment/view/', views.view_self_assessment, name='view_self_assessment'),
]

