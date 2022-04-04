from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
  return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

  def setUp(self):
    self.client = APIClient()

  def test_valid_new_user_success(self):
    """Test creating user with valid payload is successful"""
    payload = {
        'email': 'vinson@vinson.sg',
        'password': 'password123',
        'name': 'Vinson Ong',
    }
    res = self.client.post(CREATE_USER_URL, payload)
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    user = get_user_model().objects.get(**res.data)
    self.assertTrue(user.check_password(payload['password']))
    self.assertNotIn('password', res.data)

  def test_user_exists(self):
    """Tests that creating a duplicate user fails"""
    payload = {'email': 'test@vinson.sg', 'password': 'password123'}
    create_user(**payload)

    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_password_too_short(self):
    """Tests that the password must be more than 5 characters"""
    payload = {'email': 'test@vinson.sg',
               'name': 'vinson', 'password': 'pw'}
    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    user_exists = get_user_model().objects.filter(
        email=payload['email']).exists()
    self.assertFalse(user_exists)
