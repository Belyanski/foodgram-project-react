from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models

from users.models import User

MAX_LENGTH_STRING = 200
MAX_LENGTH_COLOR = 7


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_STRING,
        unique=True
    )
    color = ColorField(
        'Цвет',
        max_length=MAX_LENGTH_COLOR,
        unique=True
    )
    slug = models.SlugField(
        'Ссылка',
        max_length=MAX_LENGTH_STRING,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField('Название', max_length=MAX_LENGTH_STRING)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_STRING
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = [['name', 'measurement_unit']]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_STRING
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное время '
                              'приготовления 1 минута.'),
            MaxValueValidator(1440, message='Максимальное время '
                              'приготовления 1440 минут (1 день).')
        ]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1, message='Выберете хотя бы 1 ингредиент.'),
            MaxValueValidator(100, message='Максимальное количество '
                              'ингредиента - 100.')
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount} {self.ingredient.measurement_unit}'


class BaseRelation(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

class Favorite(BaseRelation):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

class ShoppingCart(BaseRelation):
    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
