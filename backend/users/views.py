from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from api.serializers import CustomUserSerializer, SubscribeSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.response import Response

from .models import User, Subscribe



class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'new_password': ['This field is required.']},
                            status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)

        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            if request.method == 'POST':
                if user == author:
                    data = {'errors': 'Вы не можете подписаться на себя.'}
                    return Response(data=data,
                                    status=status.HTTP_400_BAD_REQUEST)

                Subscribe.objects.create(user=user, author=author)
                serializer = SubscribeSerializer(author,
                                                 context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

            elif request.method == 'DELETE':
                subscribe = Subscribe.objects.filter(user=user, author=author)
                if subscribe.exists():
                    subscribe.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    data = {'errors': 'Вы не можете подписаться.'}
                    return Response(data=data,
                                    status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            data = {'errors': 'Вы уже подписаны.'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if user.is_authenticated:
            serializer = CustomUserSerializer(
                user,
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response({'detail': 'Учетные данные не предоставлены.'},
                            status=HTTP_401_UNAUTHORIZED)

    @me.mapping.post
    def me_post(self, request):
        return self.me(request)