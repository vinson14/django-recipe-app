from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
  """Return recipe detail URL"""
  return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Dessert'):
  """Creates and returns a sample tag"""
  return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Chicken'):
  """Creates and returns a sample ingredient"""
  return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
  """Creates and returns a sample recipe"""
  defaults = {
      'title': 'Sample Recipe Title',
      'time_minutes': 10,
      'price': 5.00
  }
  defaults.update(params)

  return Recipe.objects.create(user=user, **defaults)


class PublicRecipesApiTest(TestCase):
  """Tests the publicly available recipes API"""

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    """Tests that login is required to retrieve the recipes"""
    res = self.client.get(RECIPES_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTest(TestCase):
  """Tests that APIs that requires authentication"""

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        email='vinson@vinson.sg', password='password')
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_retrieve_recipes(self):
    """Tests retrieving a list of recipes"""
    steak = sample_recipe(user=self.user, title='Steak')
    chicken_rice = sample_recipe(user=self.user, title='Chicken Rice')

    res = self.client.get(RECIPES_URL)

    recipes = Recipe.objects.all().order_by('-id')
    serializer = RecipeSerializer(recipes, many=True)

    self.assertEqual(res.data, serializer.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)

  def test_recipes_limited_to_user(self):
    """Tests retrieving recipes for user"""
    sample_recipe(user=self.user)
    sample_recipe(user=self.user)

    another_user = get_user_model().objects.create_user(
        email='another@vinson.sg', password='password')
    sample_recipe(user=another_user)

    recipes = Recipe.objects.filter(user=self.user)
    serializer = RecipeSerializer(recipes, many=True)

    res = self.client.get(RECIPES_URL)

    self.assertEqual(res.data, serializer.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)

  def test_view_recipe_detail(self):
    """Tests viewing a detailed recipe"""
    recipe = sample_recipe(user=self.user)
    recipe.tags.add(sample_tag(user=self.user))
    recipe.ingredients.add(sample_ingredient(user=self.user))

    url = detail_url(recipe.id)
    res = self.client.get(url)

    serializer = RecipeDetailSerializer(recipe)
    self.assertEqual(res.data, serializer.data)
