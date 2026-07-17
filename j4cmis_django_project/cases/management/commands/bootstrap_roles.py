"""
One-time setup: creates a Django auth Group per UserProfile.Role (v4's exact
three roles: System Admin, National Coordinator, Regional Coordinator) with
default permissions. Run after migrate: `python manage.py bootstrap_roles`.

Region restriction for Regional Coordinators (NFR-06) is enforced at the
query layer (see cases/views.py) using UserProfile.region, not via Django
Group scoping — groups here only encode CRUD breadth, not row-level scope.
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from cases.models import UserProfile

ROLE_APP_LABEL = "cases"

ROLE_ACTIONS = {
    UserProfile.Role.SYSTEM_ADMIN: ["view", "add", "change", "delete"],
    UserProfile.Role.NATIONAL_COORDINATOR: ["view", "add", "change", "delete"],
    UserProfile.Role.REGIONAL_COORDINATOR: ["view", "add", "change"],
}


class Command(BaseCommand):
    help = "Create/update auth Groups matching the three v4 roles with default permissions."

    def handle(self, *args, **options):
        perms = Permission.objects.filter(content_type__app_label=ROLE_APP_LABEL)

        for role_value, role_label in UserProfile.Role.choices:
            group, _ = Group.objects.get_or_create(name=role_label)
            actions = ROLE_ACTIONS.get(role_value, ["view"])
            role_perms = [p for p in perms if p.codename.split("_")[0] in actions]
            group.permissions.set(role_perms)
            self.stdout.write(self.style.SUCCESS(f"Configured group '{role_label}' with {len(role_perms)} permissions."))

        self.stdout.write(self.style.SUCCESS("Done. Assign users to groups in /admin/ (Authentication and Authorization > Groups)."))
