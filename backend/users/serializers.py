from abc import ABC

import os
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """ Used to retrieve user info"""

    class Meta:
        model = User
        fields = ['uuid', 'last_login', 'email', 'username', 'first_name', 'last_name', 'phone_number',
                  'email_verified', 'phone_number_verified', 'is_superuser']


class UserProfilePatchSerializer(serializers.ModelSerializer):
    """ Used to update user info"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number']
    
    def update(self, instance, validated_data):
        if validated_data.get('email'):
            instance.email_verified = False
            instance.save()
        if validated_data.get('phone_number'):
            instance.phone_number_verified = False
            instance.save()
        
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Used to register user"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'username', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        return attrs
