from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient,
                            IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from users.models import Subscribe, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and Subscribe.objects.filter(user=user, author=obj).exists())

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', )


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and Subscribe.objects.filter(user=user, author=obj).exists())

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = (
            obj.recipes.all()[:int(limit)]
            if limit is not None else obj.recipes.all()
        )
        return SubscriptionsRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientRecipeListSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount', )


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount', )


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeListSerializer(many=True,
                                                 source='ingredient_recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and Favorite.objects.filter(user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and ShoppingCart.objects.filter(user=user,
                                                recipe=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def validate(self, data):
        self.validate_tags(data)
        self.validate_ingredients(data)
        self.validate_cooking_time(data)
        return data

    def validate_tags(self, data):
        tags = data.get('tags')
        if not tags or len(tags) == 0:
            raise serializers.ValidationError('Нужно выбрать'
                                              ' хотя бы один тег!')
        if len(set(tags)) < len(tags):
            raise serializers.ValidationError('Теги должны быть уникальными!')
        return data

    def validate_ingredients(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError('Нужно выбрать хотя бы один ингредиент!')

        if len(set((ingredient['ingredient']
                    for ingredient in ingredients))) < len(ingredients):
            raise ValidationError('Ингредиенты должны быть уникальными!')

        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if amount is None or amount <= 0:
                raise ValidationError('Количество ингредиента'
                                      ' должно быть больше нуля!')

    def validate_cooking_time(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('Время приготовления'
                                              ' должно быть больше нуля!')
        return value

    def add_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if IngredientRecipe.objects.filter(
                recipe=recipe, ingredient=ingredient_id
            ).exists():
                amount += F('amount')
            IngredientRecipe.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount})

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_recipe_list = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]

        IngredientRecipe.objects.bulk_create(ingredient_recipe_list)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data['image']
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']

        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance.tags.clear()
        instance.ingredients.clear()

        for tag in tags_data:
            instance.tags.add(tag)

        for ingredient in ingredients_data:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            ingredient_object = get_object_or_404(Ingredient,
                                                  id=ingredient_id)
            instance.ingredients.add(ingredient_object,
                                     through_defaults={'amount': amount})

        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeListSerializer(instance, context=self.context)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )
