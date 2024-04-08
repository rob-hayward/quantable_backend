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
    available_units = models.JSONField(default=list)
    default_unit = models.CharField(max_length=20)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    creator_name = models.CharField(max_length=100, default='Unknown')
    pair_id = models.CharField(max_length=100, null=True, blank=True)
    is_min = models.BooleanField(default=False)
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
        if unit_enum:
            valid_units = [unit.value for unit in unit_enum]
            if self.default_unit not in valid_units:
                raise ValueError(f"Invalid default unit for the '{self.category}' category.")
            if not all(unit in valid_units for unit in self.available_units):
                raise ValueError(f"Invalid available units for the '{self.category}' category.")

        from authentech_app.models import UserProfile  # Import here to avoid circular import
        user_profile = UserProfile.objects.filter(user=self.creator).first()
        if user_profile:
            self.creator_name = user_profile.preferred_name
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

    def freedman_diaconis_bins(self):
        votes = self.vote_set.values_list('value', flat=True)
        vote_array = np.array(votes)

        if len(vote_array) < 2:
            return []

        iqr = np.subtract(*np.percentile(vote_array, [75, 25]))
        bin_width = 2 * iqr / (len(vote_array) ** (1 / 3))

        if bin_width == 0:
            return []

        min_val = vote_array.min()
        max_val = vote_array.max()
        num_bins = int(np.ceil((max_val - min_val) / bin_width))

        bins = []
        for i in range(num_bins):
            bin_min = min_val + i * bin_width
            bin_max = bin_min + bin_width
            bin_votes = vote_array[(vote_array >= bin_min) & (vote_array < bin_max)]
            bin_count = len(bin_votes)
            bin_percentage = bin_count / len(vote_array) * 100
            bins.append({
                'bin_min': bin_min,
                'bin_max': bin_max,
                'count': bin_count,
                'percentage': bin_percentage
            })

        return bins

    def ninety_percent_vote_range(self):
        bins = self.freedman_diaconis_bins()
        if not bins:
            return None

        total_votes = sum(bin['count'] for bin in bins)
        cumulative_votes = 0
        nmin = None
        nmax = None

        for bin in bins:
            cumulative_votes += bin['count']
            cumulative_percentage = cumulative_votes / total_votes * 100

            if nmin is None and cumulative_percentage >= 5:
                nmin = bin['bin_min']

            if nmax is None and cumulative_percentage >= 95:
                nmax = bin['bin_max']
                break

        if nmin is not None and nmax is not None:
            return nmin, nmax

        return None


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


class UserQuantablePreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantable = models.ForeignKey(Quantable, on_delete=models.CASCADE)
    preferred_unit = models.CharField(max_length=20)

    class Meta:
        unique_together = ('user', 'quantable')