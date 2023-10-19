from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset TestUser password'

    def handle(self, *args, **options):
        test_user = User.objects.get(username="TestUser")
        if test_user:
            test_user.set_password("TestPassword")
            test_user.save()
            self.stdout.write(self.style.SUCCESS('Password for TestUser has been set to "TestPassword".'))
        else:
            self.stdout.write(self.style.ERROR('TestUser does not exist.'))
