import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email= os.getenv('EMAIL_ADMIN'),
            first_name='Admin',
            last_name='SkyPro',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

        user.set_password(os.getenv('PASSWORD_ADMIN'))
        user.save()
