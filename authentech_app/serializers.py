# authentech_app/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    preferred_name = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ('email', 'preferred_name')


class RegistrationChallengeSerializer(serializers.Serializer):
    # Serializer for registration challenge data
    username = serializers.CharField(max_length=150)


class RegistrationResponseSerializer(serializers.Serializer):
    # Serializer for handling registration response
    credential_id = serializers.CharField()
    public_key = serializers.CharField()
    sign_count = serializers.IntegerField()


class AuthenticationChallengeSerializer(serializers.Serializer):
    # Serializer for initiating an authentication request
    username = serializers.CharField(max_length=150)


class AuthenticationResponseSerializer(serializers.Serializer):
    # Serializer for processing authentication responses
    credential_id = serializers.CharField(max_length=200)
    authenticator_data = serializers.CharField(max_length=1024)
    client_data_json = serializers.CharField(max_length=1024)
    signature = serializers.CharField(max_length=1024)
    user_handle = serializers.CharField(required=False, max_length=200)
    raw_id = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=100)

