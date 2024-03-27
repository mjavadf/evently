from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('id', 'username', 'password', 'email', 'phone_number', 'first_name', 'last_name')
        
class CustomUserDetailSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',  'first_name', 'last_name')
        
        
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # https://django-rest-framework-simplejwt.readthedocs.io/en/latest/customizing_token_claims.html
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token