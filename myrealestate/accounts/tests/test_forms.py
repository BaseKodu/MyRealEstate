from django.test import TestCase
from django.urls import reverse
from ..forms import CustomUserCreationForm, CustomAuthenticationForm
from ..models import User, UserTypeEnums
from .factories import UserFactory
from myrealestate.companies.tests.factories import CompanyFactory
from myrealestate.companies.models import Company

class TestCustomUserCreationForm(TestCase):
    def setUp(self):
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'company_name': 'Test Company'
        }

    def test_form_valid_data(self):
        """Test form with valid data"""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_creates_user_and_company(self):
        """Test that form creates both user and company with correct relationship"""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()

        # Check user was created
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, self.valid_data['email'])
        self.assertEqual(user.username, self.valid_data['username'])

        # Check company was created and linked
        company = Company.objects.get(name=self.valid_data['company_name'])
        self.assertTrue(user.companies.filter(id=company.id).exists())

        # Check user is company owner
        user_company = user.usercompanyaccess_set.get(company=company)
        self.assertEqual(user_company.access_level, UserTypeEnums.COMPANY_OWNER)

    def test_duplicate_email(self):
        """Test form validation with duplicate email"""
        # Create a user first
        UserFactory(email=self.valid_data['email'])
        
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'This email is already registered.')

    def test_duplicate_username(self):
        """Test form validation with duplicate username"""
        UserFactory(username=self.valid_data['username'])
        
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], 'This username is already taken.')

    def test_password_mismatch(self):
        """Test form validation with mismatched passwords"""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class TestCustomAuthenticationForm(TestCase):
    def setUp(self):
        self.user = UserFactory(
            email='test@example.com',
            username='testuser'
        )
        self.user.set_password('TestPass123!')
        self.user.save()

    def test_login_with_email(self):
        """Test authentication using email"""
        form = CustomAuthenticationForm(data={
            'username': 'test@example.com',
            'password': 'TestPass123!'
        })
        self.assertTrue(form.is_valid())

    def test_login_with_username(self):
        """Test authentication using username"""
        form = CustomAuthenticationForm(data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertTrue(form.is_valid())

    def test_login_with_invalid_credentials(self):
        """Test authentication with wrong password"""
        form = CustomAuthenticationForm(data={
            'username': 'test@example.com',
            'password': 'WrongPass123!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(
            form.errors['__all__'][0],
            'Please enter a correct email/username and password.'
        )

    def test_login_with_inactive_user(self):
        """Test authentication with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        form = CustomAuthenticationForm(data={
            'username': 'test@example.com',
            'password': 'TestPass123!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(
            form.errors['__all__'][0],
            'This account is inactive.'
        )