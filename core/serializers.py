from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('id', 'username', 'password', 'email', 'phone_number', 'first_name', 'last_name')
        
class CustomUserDetailSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',  'first_name', 'last_name')