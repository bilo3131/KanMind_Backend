from rest_framework import serializers
from auth_user.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'fullname', 'email']
        
class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
        
    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        
        if pw != repeated_pw:
            raise serializers.ValidationError({"password": "Passwords must match."})
        
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({"email": "Email is already in use."})
        
        fullname = self.validated_data['fullname'].strip()
        name_parts = fullname.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        account = User(email=self.validated_data['email'], username=self.validated_data['email'], first_name=first_name, last_name=last_name)
        account.set_password(pw)
        account.save()
        UserProfile.objects.create(user=account, fullname=self.validated_data['fullname'])
        return account
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        return user