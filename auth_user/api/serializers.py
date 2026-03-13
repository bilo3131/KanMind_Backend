from rest_framework import serializers
from auth_user.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for UserProfile.
    Returns id, email (fetched from the related User), and fullname.
    Used wherever user data is embedded in other responses (board members, task assignees, etc.).
    """
    # Email is stored on the User model, not UserProfile, so we use a method field
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'fullname']


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user account.
    Accepts fullname, email, password, and repeated_password.
    Creates both a Django User and a linked UserProfile.
    Validates that passwords match and the email is not already in use.
    """
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

        # Split fullname into first_name and last_name for the User model
        fullname = self.validated_data['fullname'].strip()
        name_parts = fullname.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Use email as username since we authenticate by email
        account = User(email=self.validated_data['email'], username=self.validated_data['email'], first_name=first_name, last_name=last_name)
        account.set_password(pw)
        account.save()
        UserProfile.objects.create(user=account, fullname=self.validated_data['fullname'])
        return account


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user by email and password.
    Returns the authenticated User object on success,
    or raises a ValidationError if credentials are invalid.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Django's authenticate uses username; since username == email, this works
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        return user
