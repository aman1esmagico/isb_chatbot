from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'password')
        extra_kwargs = {
            'id': {'read_only': True}  # Ensure password is not returned in responses
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'password', 'state', 'resume', 'conversation', 'conversation_summary')
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is not returned in responses
        }