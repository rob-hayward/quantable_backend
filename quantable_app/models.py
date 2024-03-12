# quantable_app/models.py

import numpy as np
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import FloatField, Count, Avg, StdDev, Min, Max
from django.db.models.functions import Cast
from .enums import Category, CATEGORY_UNIT_MAPPING
from scipy import stats

User = get_user_model()


class Quantable(models.Model):
    question = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices())
    unit = models.CharField(max_length=20)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    creator_name = models.CharField(max_length=100, default='Unknown')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vote_count = models.IntegerField(default=0)
    vote_average = models.FloatField(null=True)
    vote_median = models.FloatField(null=True)
    vote_stddev = models.FloatField(null=True)
    vote_q1 = models.FloatField(null=True)
    vote_q3 = models.FloatField(null=True)
    vote_iqr = models.FloatField(null=True)
    vote_min = models.FloatField(null=True)
    vote_max = models.FloatField(null=True)
    vote_skewness = models.FloatField(null=True)

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        unit_enum = CATEGORY_UNIT_MAPPING.get(Category(self.category))
        if unit_enum and self.unit not in [unit.value for unit in unit_enum]:
            raise ValueError(f"Invalid unit for the '{self.category}' category.")
        super().save(*args, **kwargs)

    def update_vote_data_markers(self):
        votes = self.vote_set.values_list('value', flat=True)
        vote_array = np.array(votes)

        self.vote_count = len(vote_array)
        self.vote_average = np.mean(vote_array) if self.vote_count > 0 else None
        self.vote_median = np.median(vote_array) if self.vote_count > 0 else None
        self.vote_stddev = np.std(vote_array) if self.vote_count > 1 else None
        self.vote_q1 = np.percentile(vote_array, 25) if self.vote_count > 0 else None
        self.vote_q3 = np.percentile(vote_array, 75) if self.vote_count > 0 else None
        self.vote_iqr = self.vote_q3 - self.vote_q1 if self.vote_count > 0 else None
        self.vote_min = np.min(vote_array) if self.vote_count > 0 else None
        self.vote_max = np.max(vote_array) if self.vote_count > 0 else None
        self.vote_skewness = stats.skew(vote_array) if self.vote_count > 1 else None

        self.save(update_fields=[
            'vote_count', 'vote_average', 'vote_median', 'vote_stddev',
            'vote_q1', 'vote_q3', 'vote_iqr', 'vote_min', 'vote_max', 'vote_skewness'
        ])

    def vote_data_for_d3(self):
        vote_data = self.vote_set.annotate(
            value_float=Cast('value', FloatField())
        ).values('value_float').annotate(count=Count('value_float')).order_by('value_float')

        return [{
            'value': entry['value_float'],
            'count': entry['count']
        } for entry in vote_data]


class Vote(models.Model):
    quantable = models.ForeignKey(Quantable, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('quantable', 'user')

    def __str__(self):
        return f"{self.user.username}'s vote on {self.quantable.question}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.quantable.update_vote_data_markers()