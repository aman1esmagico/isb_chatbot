from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from user.serializers import UserSerializer, UserDetailsSerializer
from user.models import User


class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        name = request.data['name']
        password = request.data['password']
        print(request.data)

        if name and password:
            user, created = User.objects.get_or_create(name=name, defaults={"password": password})
        else:
            return Response({"detail": "Invalid inputs"}, status=status.HTTP_400_BAD_REQUEST)
        print("herehere")
        if created:
            user.conversation=[]
            user.save()
        print(user)
        return Response(UserDetailsSerializer(user).data, status=status.HTTP_200_OK)


class GreetView(APIView):
    def get(self, request):
        return Response({"message": "Hello user"}, status=status.HTTP_200_OK)
