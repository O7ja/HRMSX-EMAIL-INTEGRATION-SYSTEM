import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_integration_system.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserRole

print("=" * 60)
print("FIXING MISSING USER ROLES")
print("=" * 60)

users_without_role = User.objects.filter(role_profile__isnull=True)
print(f"\nUsers without roles: {users_without_role.count()}\n")

for user in users_without_role:
    role = UserRole.objects.create(
        user=user,
        role='employee'  # Default to employee
    )
    print(f"Created role for: {user.username} -> {role.role}")

print("\n" + "=" * 60)
print("VERIFICATION - ALL USERS NOW:")
print("=" * 60 + "\n")

users = User.objects.all()
for u in users:
    role = u.role_profile.role if hasattr(u, 'role_profile') else "NO ROLE"
    print(f"{u.username:15} | {u.get_full_name():20} | Role: {role}")

print("\n" + "=" * 60)
