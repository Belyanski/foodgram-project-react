import csv

from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .mixins import RetrieveListViewSet
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer)


# Я искренне пытался сделать через ListAPIView
# Но посыпались функции с декоратором @action :( с таким трейсбеком
# AttributeError: type object
# 'CustomUserViewSet' has no attribute 'get_extra_actions'
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
                user, context=self.get_serializer_context()
                )
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response({'detail': 'Учетные данные не предоставлены.'},
                            status=HTTP_401_UNAUTHORIZED)

    @me.mapping.post
    def me_post(self, request):
        return self.me(request)


class TagsViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = (IsAuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_update(self, serializer):
        serializer.save()

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if not in_favorite:
                favorite = Favorite.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(favorite.recipe)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not in_favorite:
                data = {'errors': 'Такого рецепта нет в избранных.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping_cart = ShoppingCart.objects.filter(user=user,
                                                       recipe=recipe)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if not in_shopping_cart:
                shopping_cart = ShoppingCart.objects.create(user=user,
                                                            recipe=recipe)
                serializer = ShoppingCartSerializer(shopping_cart.recipe)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not in_shopping_cart:
                data = {'errors': 'Такой рецепта нет в списке покупок.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать список покупок для текущего пользователя."""
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        recipes = Recipe.objects.filter(author=user)

        ingredients = IngredientRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'ingredient_amount'
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="Shoppingcart.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(ingredients):
            writer.writerow(item)
        return response
