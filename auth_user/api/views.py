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

def get_user_data(user, token):
    return {
        'token': token.key,
        'fullname': user.userprofile.fullname,
        'email': user.email,
        'user_id': user.userprofile.id
    }

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class RegistrationView(APIView):
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
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            data = get_user_data(user, token)
            return Response(get_user_data(user, token), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
class EmailCheckView(APIView):
    
    def get(self, request):
        email = request.query_params.get('email')
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