from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserRole


@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    """
    Automatically create a UserRole for new users.
    Default role is 'employee' - can be changed in admin.
    """
    if created:
        # Check if UserRole already exists
        if not hasattr(instance, 'role_profile'):
            UserRole.objects.get_or_create(
                user=instance,
                defaults={'role': 'employee'}
            )


@receiver(post_save, sender=User)
def save_user_role(sender, instance, **kwargs):
    """
    Save UserRole when User is saved.
    """
    if hasattr(instance, 'role_profile'):
        instance.role_profile.save()
