import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_integration_system.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserRole

print("=" * 60)
print("CHECKING USER ROLES")
print("=" * 60)

users = User.objects.all()
print(f"\nTotal users: {users.count()}\n")

for u in users:
    has_role = hasattr(u, 'role_profile')
    role = u.role_profile.role if has_role else "NO ROLE"
    print(f"{u.username:15} | {u.get_full_name():20} | Role: {role}")

print("\n" + "=" * 60)
