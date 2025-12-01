"""
Context processors for users app
Provides user role information to templates safely
"""
from django.contrib.auth.models import AnonymousUser
from .models import UserRole


def user_role(request):
    """Add user role to template context"""
    if request.user.is_authenticated:
        try:
            role_obj = UserRole.objects.get(user=request.user)
            return {
                'user_role': role_obj.role,
                'user_role_obj': role_obj,
            }
        except UserRole.DoesNotExist:
            return {
                'user_role': None,
                'user_role_obj': None,
            }
    return {
        'user_role': None,
        'user_role_obj': None,
    }
