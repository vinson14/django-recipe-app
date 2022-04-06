from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
    payload = {'email': 'test@vinson.sg',
               'name': 'vinson',
               'password': 'password123'}
    create_user(**payload)

    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_password_too_short(self):
    """Tests that the password must be more than 5 characters"""
    payload = {'email': 'test@vinson.sg',
               'name': 'vinson',
               'password': 'pw'}
    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    user_exists = get_user_model().objects.filter(
        email=payload['email']).exists()
    self.assertFalse(user_exists)

  def test_create_token_for_user(self):
    """Test that a token is created for the user"""
    payload = {'email': 'vinson@vinson.sg', 'password': 'password'}
    create_user(**payload)
    res = self.client.post(TOKEN_URL, payload)

    self.assertIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)

  def test_no_token_for_invalid_credentials(self):
    """Tests that no token is returned for invalid credentials"""
    create_user(email="vinson@vinson.sg", password="password")
    payload = {'email': 'vinson@vinson.sg', 'password': 'passworddd'}
    res = self.client.post(TOKEN_URL, payload)

    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_no_token_for_invalid_user(self):
    """Tests that no token is return for a user that does not exist"""
    payload = {'email': 'vinson@vinson.sg', 'password': 'password'}
    res = self.client.post(TOKEN_URL, payload)

    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_no_token_for_missing_password(self):
    """Tests that no token is return when no password is given"""
    payload = {'email': 'vinson@vinson.sg', 'password': ''}
    res = self.client.post(TOKEN_URL, payload)
    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_retrieve_user_unauthorized(self):
    """Tests that an unauthorized request fails to retrieve a user"""
    res = self.client.get(ME_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
  """Tests API Requests that require authentication"""

  def setUp(self):
    self.user = create_user(
        email='email@email.com',
        password='password',
        name='vinson'
    )
    self.client = APIClient()
    self.client.force_authenticate(user=self.user)

  def test_retrieve_profile_success(self):
    """Tests retrieving profile for logged in user"""
    res = self.client.get(ME_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data, {'name': self.user.name, 'email': self.user.email})

  def test_post_me_not_allowed(self):
    """Tests that post requests are not allowed for ME endpoint"""
    res = self.client.post(ME_URL, {})

    self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_update_user_profile(self):
    """Tests that the user_profile can be updated"""
    payload = {'name': 'new name', 'password': 'new password'}

    res = self.client.patch(ME_URL, payload)
    self.user.refresh_from_db()

    self.assertEqual(self.user.name, payload['name'])
    self.assertTrue(self.user.check_password(payload['password']))
    self.assertEqual(res.status_code, status.HTTP_200_OK)
