from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
  """Tests the publicly available Tags APIs"""

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    """Tests that login is required to get the tags"""
    res = self.client.get(TAGS_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
  """Tests the Tags APIs that are only available to authenticated users"""

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        email='vinson@vinson.sg', password='password')
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_retrieve_tags(self):
    """Test retrieving tags"""
    Tag.objects.create(user=self.user, name='Vegan')
    Tag.objects.create(user=self.user, name='Dessert')

    res = self.client.get(TAGS_URL)

    tags = Tag.objects.all().order_by('-name')
    serializer = TagSerializer(tags, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_tags_limited_to_user(self):
    """Tests that only tags that belongs to user is retrieved"""
    Tag.objects.create(user=self.user, name='Vegan')
    Tag.objects.create(user=self.user, name='Dessert')
    another_user = get_user_model().objects.create_user(
        email='another@vinson.sg', password='password')
    Tag.objects.create(user=another_user, name='AnotherUser')

    res = self.client.get(TAGS_URL)

    tags = Tag.objects.filter(user=self.user).order_by('-name')
    serializer = TagSerializer(tags, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)
