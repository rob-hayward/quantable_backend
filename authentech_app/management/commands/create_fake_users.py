# authentech_app/management/commands/create_fake_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from authentech_app.models import UserProfile


class Command(BaseCommand):
    help = 'Creates fake users with UserProfiles'

    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int, help='Number of fake users to create')

    def handle(self, *args, **options):
        num_users = options['num_users']
        fake = Faker()

        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            first_name = fake.first_name()
            last_name = fake.last_name()
            preferred_name = f"{first_name} {last_name}"

            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=first_name, last_name=last_name)
            UserProfile.objects.create(user=user, preferred_name=preferred_name)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_users} fake users.'))