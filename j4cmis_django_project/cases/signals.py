from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Every auth.User gets a matching UserProfile (role/region) automatically,
    so admins never have to remember a second setup step when adding staff."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
