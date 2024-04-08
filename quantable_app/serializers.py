# quantable_app/serializers.py

from rest_framework import serializers
from .models import Quantable, Vote, UserQuantablePreference
from django.contrib.auth import get_user_model
from .enums import Category

User = get_user_model()


class QuantableSerializer(serializers.ModelSerializer):
    available_units = serializers.ListField(child=serializers.CharField())
    default_unit = serializers.CharField()
    pair_id = serializers.CharField(required=False, allow_null=True)
    is_min = serializers.BooleanField(required=False)
    vote_values = serializers.SerializerMethodField()

    class Meta:
        model = Quantable
        fields = ['id', 'question', 'category', 'available_units', 'default_unit', 'creator', 'creator_name',
                  'pair_id', 'is_min', 'created_at', 'updated_at',
                  'vote_count', 'vote_average', 'vote_median', 'vote_stddev', 'vote_q1', 'vote_q3',
                  'vote_iqr', 'vote_min', 'vote_max', 'vote_skewness', 'vote_values']
        read_only_fields = ['creator', 'creator_name', 'created_at', 'updated_at', 'vote_count', 'vote_average',
                            'vote_median', 'vote_stddev', 'vote_q1', 'vote_q3', 'vote_iqr',
                            'vote_min', 'vote_max', 'vote_skewness', 'vote_values']

    def get_vote_values(self, obj):
        return obj.vote_set.values_list('value', flat=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['creator'] = instance.creator.id
        print(f"QuantableSerializer - to_representation - Instance: {instance}")
        print(f"QuantableSerializer - to_representation - Representation: {representation}")
        return representation


class QuantablePairSerializer(serializers.Serializer):
    min_quantable = QuantableSerializer()
    max_quantable = QuantableSerializer()

    def to_representation(self, instance):
        print(f"QuantablePairSerializer - to_representation - Instance: {instance}")
        min_quantable_data = instance['min_quantable']
        max_quantable_data = instance['max_quantable']

        representation = {
            'min_quantable': min_quantable_data,
            'max_quantable': max_quantable_data,
        }
        print(f"QuantablePairSerializer - to_representation - Representation: {representation}")
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