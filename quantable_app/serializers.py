# quantable_app/serializers.py

from rest_framework import serializers
from .models import Quantable, Vote
from .enums import Category


class QuantableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quantable
        fields = ['id', 'question', 'category', 'unit', 'creator', 'created_at', 'updated_at',
                  'vote_count', 'vote_average', 'vote_median', 'vote_stddev', 'vote_q1', 'vote_q3',
                  'vote_iqr', 'vote_min', 'vote_max', 'vote_skewness']
        read_only_fields = ['creator', 'created_at', 'updated_at', 'vote_count', 'vote_average',
                            'vote_median', 'vote_stddev', 'vote_q1', 'vote_q3', 'vote_iqr',
                            'vote_min', 'vote_max', 'vote_skewness']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'quantable', 'user', 'value', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()

    class Meta:
        fields = ['name', 'value']