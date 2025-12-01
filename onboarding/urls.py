from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.onboarding_status, name='onboarding_status'),
    path('checklist/<int:item_id>/update/', views.update_checklist_item, name='update_checklist_item'),
    path('offboarding/status/', views.offboarding_status, name='offboarding_status'),
    path('offboarding/checklist/<int:item_id>/update/', views.update_offboarding_checklist_item, name='update_offboarding_checklist_item'),
    path('new-employee/', views.new_employee_onboarding, name='new_employee_onboarding'),
    path('initiate-offboarding/<int:employee_id>/', views.initiate_offboarding, name='initiate_offboarding'),
]
