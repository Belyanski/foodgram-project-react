from django.contrib import admin

from .models import (Favorite,
                     Ingredient,
                     IngredientRecipe,
                     Recipe,
                     ShoppingCart,
                     Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Модель Tag в админке."""
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    """Модель IngredientRecipe в админке."""
    model = IngredientRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Модель Ingredient в админке."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (IngredientRecipeInline,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Модель Recipe в админке."""
    list_display = ('id', 'name', 'author')
    search_fields = ('author', 'name', 'tags')
    inlines = (IngredientRecipeInline,)

    def is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Модель Favorite в админке."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Модель ShoppingCart в админке."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
