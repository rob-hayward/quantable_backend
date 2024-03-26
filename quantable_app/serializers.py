# quantable_app/serializers.py

from rest_framework import serializers
from .models import Quantable, Vote, UserQuantablePreference
from .enums import Category


class QuantableSerializer(serializers.ModelSerializer):
    available_units = serializers.ListField(child=serializers.CharField())
    default_unit = serializers.CharField()
    vote_values = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Quantable
        fields = ['id', 'question', 'category', 'available_units', 'default_unit', 'creator', 'creator_name', 'created_at', 'updated_at', 'user_vote',
                  'vote_count', 'vote_average', 'vote_median', 'vote_stddev', 'vote_q1', 'vote_q3',
                  'vote_iqr', 'vote_min', 'vote_max', 'vote_skewness', 'vote_values']
        read_only_fields = ['creator', 'creator_name', 'created_at', 'updated_at', 'user_vote', 'vote_count', 'vote_average',
                            'vote_median', 'vote_stddev', 'vote_q1', 'vote_q3', 'vote_iqr',
                            'vote_min', 'vote_max', 'vote_skewness', 'vote_values']

    def get_vote_values(self, obj):
        return obj.vote_set.values_list('value', flat=True)

    def get_user_vote(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            vote = obj.vote_set.filter(user=user).first()
            if vote:
                return vote.value
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


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


class UserQuantablePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuantablePreference
        fields = ['user', 'quantable', 'preferred_unit']