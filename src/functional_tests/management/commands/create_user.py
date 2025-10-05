from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("password")

    def handle(self, *args, **options):
        create_user(options["email"], options["password"])
        self.stdout.write("OK")


def create_user(email, password):
    user = User.objects.create(email=email)
    user.set_password(password)
    user.save()
