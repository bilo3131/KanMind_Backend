from rest_framework import generics
from auth_user.models import UserProfile
from auth_user.api.serializers import UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email


def get_user_data(user, token):
    """
    Helper function that returns a standardized dict with user info and auth token.
    Used by both RegistrationView and LoginView.
    """
    return {
        'token': token.key,
        'fullname': user.userprofile.fullname,
        'email': user.email,
        'user_id': user.userprofile.id
    }


class UserProfileList(generics.ListCreateAPIView):
    """
    GET  /api/profiles/ — Returns a list of all user profiles.
    POST /api/profiles/ — Creates a new user profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/profiles/{pk}/ — Returns a single user profile.
    PATCH  /api/profiles/{pk}/ — Updates a user profile.
    DELETE /api/profiles/{pk}/ — Deletes a user profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
    """
    POST /api/registration/ — Registers a new user account.
    Returns token and user data on success.
    No authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = get_user_data(saved_account, token)
        else:
            data = serializer.errors
        return Response(data)


class LoginView(APIView):
    """
    POST /api/login/ — Authenticates a user by email and password.
    Returns token and user data on success (200).
    Returns 400 if credentials are invalid.
    No authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            data = get_user_data(user, token)
            return Response(get_user_data(user, token), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailCheckView(APIView):
    """
    GET /api/email-check/?email={email} — Looks up a user by email address.
    Returns the user's id, fullname, and email on success (200).
    Returns 400 if the email format is invalid.
    Returns 404 if no user with that email exists.
    Requires authentication.
    """
    def get(self, request):
        email = request.query_params.get('email')

        # Validate the email format before querying the database
        try:
            validate_email(email)
        except DjangoValidationError:
            return Response({'detail': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            data = {
                'id': user.userprofile.id,
                'fullname': user.userprofile.fullname,
                'email': user.email
            }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
