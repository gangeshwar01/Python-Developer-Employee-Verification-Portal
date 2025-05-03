from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_portal.models import Employee, Task, Certificate
from django.utils import timezone
import os
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **kwargs):
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create test employees
        employees = [
            {
                'emp_id': 'EMP001',
                'name': 'John Doe',
                'designation': 'Software Engineer',
                'join_date': datetime.now() - timedelta(days=365)
            },
            {
                'emp_id': 'EMP002',
                'name': 'Jane Smith',
                'designation': 'Project Manager',
                'join_date': datetime.now() - timedelta(days=180)
            },
            {
                'emp_id': 'EMP003',
                'name': 'Mike Johnson',
                'designation': 'Senior Developer',
                'join_date': datetime.now() - timedelta(days=90)
            }
        ]

        for emp_data in employees:
            employee, created = Employee.objects.get_or_create(
                emp_id=emp_data['emp_id'],
                defaults=emp_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created employee: {employee.name}'))

                # Create some tasks for the employee
                tasks = [
                    {
                        'title': 'Project Setup',
                        'description': 'Initial project setup and configuration',
                        'date': datetime.now() - timedelta(days=30)
                    },
                    {
                        'title': 'Code Review',
                        'description': 'Review and approve pull requests',
                        'date': datetime.now() - timedelta(days=15)
                    },
                    {
                        'title': 'Bug Fixing',
                        'description': 'Fix critical production issues',
                        'date': datetime.now() - timedelta(days=7)
                    }
                ]

                for task_data in tasks:
                    Task.objects.create(employee=employee, **task_data)

                # Create some certificates for the employee
                certificates = [
                    {
                        'title': 'Python Certification',
                        'status': 'verified',
                        'verified_by': admin_user,
                        'verification_date': datetime.now() - timedelta(days=60)
                    },
                    {
                        'title': 'Django Certification',
                        'status': 'pending'
                    },
                    {
                        'title': 'AWS Certification',
                        'status': 'rejected',
                        'verified_by': admin_user,
                        'verification_date': datetime.now() - timedelta(days=30),
                        'rejection_reason': 'Certificate appears to be forged'
                    }
                ]

                for cert_data in certificates:
                    Certificate.objects.create(employee=employee, **cert_data)

        self.stdout.write(self.style.SUCCESS('Successfully populated database with test data')) 