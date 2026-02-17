"""
Management command to seed initial roles.
"""

from django.core.management.base import BaseCommand
from apps.authentication.models import Role


class Command(BaseCommand):
    help = 'Seed initial roles (Admin, User)'
    
    def handle(self, *args, **options):
        """Create initial roles."""
        roles_data = [
            {
                'name': 'Admin',
                'description': 'Administrator with full permissions'
            },
            {
                'name': 'User',
                'description': 'Regular user with standard permissions'
            },
        ]
        
        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Role already exists: {role.name}')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully created {created_count} role(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ All roles already exist')
            )
