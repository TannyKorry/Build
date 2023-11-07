import json
from distutils.util import strtobool

from django.urls import reverse
# from .forms import SignUpForm, LogInForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django_filters.rest_framework import DjangoFilterBackend
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from ujson import loads as load_json
from yaml import load as load_yaml, Loader

from .models import Contact, ConfirmEmailToken
from .serializers import UserSerializer, ContactSerializer
from .signals import new_user_registered, new_order
class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):

            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])

            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}}, status=403)
            else:
                # проверяем данные для уникальности имени пользователя
                # request.data._mutable = True
                # request.data.update(request.data)
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    new_user_registered.send(sender=self.__class__, user_id=user.id)
                    return JsonResponse({'Status': True}, status=201)
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors}, status=403)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=400)

#
# {
#    "First_name": "Азамат",
#    "last_name": "Искаков",
#    "email": "a.iskakov1989@gmail.com",
#    "password": "qwer1234A",
#    "company": "asdads",
#    "position": "345345",
# }