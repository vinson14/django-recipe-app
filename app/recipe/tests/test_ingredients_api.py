from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
  """Tests the public available ingredients API"""

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    """Tests that lgoin is required to get the ingredients"""
    res = self.client.get(INGREDIENTS_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        email='vinson@vinson.sg', password='password'
    )
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_retrieve_ingredients(self):
    """Tests retrieving ingredients"""
    Ingredient.objects.create(user=self.user, name='Cucumber')
    Ingredient.objects.create(user=self.user, name='Potato')

    res = self.client.get(INGREDIENTS_URL)

    ingredients = Ingredient.objects.all().order_by('-name')
    serializer = IngredientSerializer(ingredients, many=True)

    self.assertEqual(res.data, serializer.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)

  def test_ingredients_limited_to_user(self):
    """Tests that only the authenticated user's ingredients are retrieved"""
    Ingredient.objects.create(user=self.user, name='Cucumber')
    Ingredient.objects.create(user=self.user, name='Kale')

    another_user = get_user_model().objects.create_user(
        user='another@vinson.sg', password='password')
    Ingredient.objects.create(user=another_user, name='Another Ingredient')

    ingredients = Ingredient.objects.filter(user=self.user).order_by('name')
    serializer = IngredientSerializer(ingredients, many=True)

    res = self.client.get(INGREDIENTS_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)
