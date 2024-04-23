# quantable_app/management/commands/load_sample_data.py
import random
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quantable_app.models import Quantable, Vote


class Command(BaseCommand):
    help = 'Loads sample data and generates realistic votes'

    def handle(self, *args, **options):
        # Load sample quantables
        quantables = [
            {
                "question": "What do you believe is the minimum amount of money that a person needs each month to avoid living in deprivation?",
                "category": "currency",
                "available_units": ["GBP", "USD", "EUR"],
                "default_unit": "GBP",
                "creator": User.objects.get(pk=1),
                "pair_id": "pair_1",
                "is_min": True
            },
            {
                "question": "What do you believe is the maximum amount of money that a person needs each month to avoid living in excess?",
                "category": "currency",
                "available_units": ["GBP", "USD", "EUR"],
                "default_unit": "GBP",
                "creator": User.objects.get(pk=1),
                "pair_id": "pair_1",
                "is_min": False
            },
            {
                "question": "What is the smallest home size to avoid living in deprivation?",
                "category": "area",
                "available_units": ["m²", "ft²"],
                "default_unit": "m²",
                "creator": User.objects.get(pk=2),
                "pair_id": "pair_2",
                "is_min": True
            },
            {
                "question": "What is the largest home size to avoid living in excess?",
                "category": "area",
                "available_units": ["m²", "ft²"],
                "default_unit": "m²",
                "creator": User.objects.get(pk=2),
                "pair_id": "pair_2",
                "is_min": False
            },
            {
                "question": "What should be the minimum age of consent to have sex?",
                "category": "time",
                "available_units": ["year"],
                "default_unit": "year",
                "creator": User.objects.get(pk=3),
                "pair_id": None,
                "is_min": False
            },
            {
                "question": "What is the ideal temperature for a comfortable living environment?",
                "category": "temperature",
                "available_units": ["°C", "°F"],
                "default_unit": "°C",
                "creator": User.objects.get(pk=4),
                "pair_id": None,
                "is_min": False
            },
            {
                "question": "What is the minimum number of hours of sleep per night required for optimal health?",
                "category": "time",
                "available_units": ["h"],
                "default_unit": "h",
                "creator": User.objects.get(pk=5),
                "pair_id": None,
                "is_min": False
            },
            {
                "question": "What is the minimum amount of water a person should drink per day?",
                "category": "volume",
                "available_units": ["l", "gal"],
                "default_unit": "l",
                "creator": User.objects.get(pk=6),
                "pair_id": None,
                "is_min": False
            }
        ]

        for quantable_data in quantables:
            quantable, created = Quantable.objects.get_or_create(**quantable_data)

            # Delete existing votes for the quantable
            Vote.objects.filter(quantable=quantable).delete()

            # Generate realistic votes for the quantable
            num_votes = random.randint(50, 100)  # Random number of votes between 50 and 100
            users = list(User.objects.all())
            random.shuffle(users)  # Shuffle the users randomly

            if quantable.category == 'currency':
                if quantable.is_min:
                    vote_mean = 800  # Lower mean for minimum currency quantable
                    vote_stddev = 100
                else:
                    vote_mean = 4000  # Higher mean for maximum currency quantable
                    vote_stddev = 500
            elif quantable.category == 'area':
                if quantable.is_min:
                    vote_mean = 30  # Lower mean for minimum area quantable
                    vote_stddev = 5
                else:
                    vote_mean = 150  # Higher mean for maximum area quantable
                    vote_stddev = 20
            else:
                vote_mean = 40
                vote_stddev = 10

            for user in users[:num_votes]:
                value = np.random.normal(vote_mean, vote_stddev)
                Vote.objects.create(quantable=quantable, user=user, value=value)

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data and generated realistic votes.'))