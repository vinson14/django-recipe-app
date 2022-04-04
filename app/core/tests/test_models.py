from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

  mock_email = "vinson@vinson.sg"
  mock_password = "p@$$w0rd12345"

  def test_create_user_with_email_successful(self):
    """Test creating a new user with mock email is successful"""
    user = get_user_model().objects.create_user(
        email=self.mock_email,
        password=self.mock_password
    )

    self.assertEqual(user.email, self.mock_email)
    self.assertTrue(user.check_password(self.mock_password))

  def test_new_user_email_normalized(self):
    email = 'vinson@vInsON.Sg'
    user = get_user_model().objects.create_user(
        email=email,
        password=self.mock_password
    )

    self.assertEqual(user.email, email.lower())

  def test_new_user_no_email_error(self):
    """Tests that an error is thrown when no email is provided"""
    with self.assertRaises(ValueError):
      user = get_user_model().objects.create_user(
          email=None,
          password=self.mock_password
      )

  def test_create_new_super_user(self):
    """Tests that a super user is created properly"""
    user = get_user_model().objects.create_superuser(
        email=self.mock_email,
        password=self.mock_password
    )
    self.assertTrue(user.is_superuser)
    self.assertTrue(user.is_staff)
