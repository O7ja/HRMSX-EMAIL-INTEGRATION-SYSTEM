from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from users.models import UserRole, EmployeeProfile
from leave.models import LeaveType, LeaveBalance
from onboarding.models import Onboarding, OnboardingChecklist


class Command(BaseCommand):
    help = 'Create demo users and data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo users...'))
        
        # Create leave types
        leave_types_data = [
            ('Vacation', 'Vacation leave'),
            ('Sick Leave', 'Sick leave for medical reasons'),
            ('Personal Leave', 'Personal leave for emergencies'),
            ('Maternity Leave', 'Maternity leave'),
            ('Paternity Leave', 'Paternity leave'),
        ]
        
        for name, desc in leave_types_data:
            LeaveType.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'is_active': True}
            )
        self.stdout.write('✓ Leave types created')
        
        # Create HR user
        hr_user, created = User.objects.get_or_create(
            username='hr1',
            defaults={
                'first_name': 'HR',
                'last_name': 'Manager',
                'email': 'hr@company.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            hr_user.set_password('password123')
            hr_user.save()
        
        hr_role, _ = UserRole.objects.get_or_create(
            user=hr_user,
            defaults={
                'role': 'hr',
                'department': 'Human Resources',
                'phone': '9876543210',
            }
        )
        self.stdout.write('✓ HR user created: hr1 / password123')
        
        # Create Manager user
        manager_user, created = User.objects.get_or_create(
            username='manager1',
            defaults={
                'first_name': 'John',
                'last_name': 'Manager',
                'email': 'manager@company.com',
            }
        )
        if created:
            manager_user.set_password('password123')
            manager_user.save()
        
        manager_role, _ = UserRole.objects.get_or_create(
            user=manager_user,
            defaults={
                'role': 'manager',
                'department': 'Engineering',
                'phone': '9876543211',
            }
        )
        self.stdout.write('✓ Manager user created: manager1 / password123')
        
        # Create Employee users
        for i in range(1, 4):
            emp_user, created = User.objects.get_or_create(
                username=f'emp{i}',
                defaults={
                    'first_name': f'Employee',
                    'last_name': f'{i}',
                    'email': f'emp{i}@company.com',
                }
            )
            if created:
                emp_user.set_password('password123')
                emp_user.save()
            
            emp_role, _ = UserRole.objects.get_or_create(
                user=emp_user,
                defaults={
                    'role': 'employee',
                    'department': 'Engineering',
                    'phone': f'98765432{10+i}',
                    'manager': manager_user,
                }
            )
            
            # Create employee profile
            emp_profile, _ = EmployeeProfile.objects.get_or_create(
                user=emp_user,
                defaults={
                    'employee_id': f'EMP{1000+i}',
                    'date_of_joining': date(2023, 1, 15),
                    'leave_balance': 20,
                    'emergency_contact': f'90000000{i}0',
                    'address': f'{i} Main Street, City',
                    'is_active_employee': True,
                }
            )
            
            # Create onboarding record
            onboarding, _ = Onboarding.objects.get_or_create(
                employee=emp_user,
                defaults={'status': 'completed', 'welcome_email_sent': True}
            )
            
            # Create leave balance for each leave type
            for leave_type in LeaveType.objects.all():
                LeaveBalance.objects.get_or_create(
                    employee=emp_user,
                    leave_type=leave_type,
                    year=timezone.now().year,
                    defaults={'total_balance': 20, 'used_balance': 0}
                )
            
            self.stdout.write(f'✓ Employee user created: emp{i} / password123')
        
        self.stdout.write(self.style.SUCCESS('\n✅ All demo data created successfully!'))
        self.stdout.write(self.style.WARNING('\nDemo Accounts:'))
        self.stdout.write('  Employee: emp1 / password123')
        self.stdout.write('  Manager: manager1 / password123')
        self.stdout.write('  HR: hr1 / password123')
