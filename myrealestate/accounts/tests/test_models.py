from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import User, UserTypeEnums
from .factories import UserFactory

class TestUserModel(TestCase):
    def setUp(self):
        """Set up data for all test methods"""
        self.user = UserFactory()

    def test_create_user(self):
        """Test creating a regular user"""
        self.assertIsNotNone(self.user.pk)
        self.assertIsNotNone(self.user.email)
        self.assertIsNotNone(self.user.username)
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.email, 'admin@example.com')

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without email raises error"""
        with self.assertRaisesMessage(ValueError, 'Email is required'):
            User.objects.create_user(email='', password='testpass123')

    def test_user_str_method(self):
        """Test the string representation of User model"""
        user = UserFactory(email='test@example.com')
        self.assertEqual(str(user), 'test@example.com')

    def test_email_is_normalized(self):
        """Test email normalization"""
        email = 'Test@EXAMPLE.com'
        user = User.objects.create_user(email=email, password='testpass123')
        self.assertEqual(user.email, 'Test@example.com')