from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname','name', 'identity', 'sex', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # 自动加密
        return super().create(validated_data)