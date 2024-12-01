from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from ..models import User, UserTypeEnums
from .factories import UserFactory
from myrealestate.companies.models import Company
from myrealestate.companies.tests.factories import CompanyFactory


class TestRegisterView(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.home_url = reverse('home')
        self.valid_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'company_name': 'New Company'
        }

    def test_register_page_load(self):
        """Test GET request to register page"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_success(self):
        """Test successful registration"""
        response = self.client.post(self.register_url, self.valid_data)
        
        # Check redirect to login page
        self.assertRedirects(response, self.login_url)
        
        # Check user was created
        self.assertTrue(User.objects.filter(email=self.valid_data['email']).exists())
        user = User.objects.get(email=self.valid_data['email'])
        
        # Check company was created
        company = Company.objects.get(name=self.valid_data['company_name'])
        self.assertTrue(user.companies.filter(id=company.id).exists())
        
        # Check user is company owner
        user_company = user.usercompanyaccess_set.get(company=company)
        self.assertEqual(user_company.access_level, UserTypeEnums.COMPANY_OWNER)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Account created successfully! Please login.')

    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=invalid_data['email']).exists())
        
        # Access form errors from context
        form = response.context['form']
        self.assertIn('password2', form.errors)
        self.assertEqual(
            form.errors['password2'][0],
            "The two password fields didn’t match."
        )

    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        UserFactory(email=self.valid_data['email'])
        
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        
        # Access form errors from context
        form = response.context['form']
        self.assertIn('email', form.errors)
        self.assertEqual(
            form.errors['email'][0],
            'This email is already registered.'
        )

    def test_authenticated_user_redirect(self):
        """Test that authenticated users are redirected to home"""
        user = UserFactory()
        self.client.force_login(user)
        
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.home_url)


class TestCustomLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.home_url = reverse('home')
        
        # Create test user
        self.user = UserFactory(email='test@example.com', username='testuser')
        self.user.set_password('TestPass123!')
        self.user.save()
        
        self.valid_credentials = {
            'username': 'test@example.com',
            'password': 'TestPass123!'
        }

    def test_login_page_load(self):
        """Test GET request to login page"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_success_with_email(self):
        """Test successful login using email"""
        response = self.client.post(self.login_url, self.valid_credentials)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_success_with_username(self):
        """Test successful login using username"""
        credentials = self.valid_credentials.copy()
        credentials['username'] = 'testuser'
        
        response = self.client.post(self.login_url, credentials)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_credentials = self.valid_credentials.copy()
        invalid_credentials['password'] = 'WrongPass123!'
        
        response = self.client.post(self.login_url, invalid_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Invalid username or password')

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, self.valid_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    # In TestCustomLoginView class, add this new test:
    def test_login_sets_company_session(self):
        """Test that logging in sets the company session data"""
        # Create a company and associate it with the user
        company = CompanyFactory(
            name="Test Company",
            contact_email="company@test.com",
            contact_phone="1234567890"
        )
        self.user.companies.add(company, through_defaults={'access_level': UserTypeEnums.COMPANY_OWNER})
        
        response = self.client.post(self.login_url, self.valid_credentials, follow=True)
        
        # Check if company is in session
        self.assertIn('company', self.client.session)
        self.assertIn('current_company_id', self.client.session)
        
        # Verify session data
        company_data = self.client.session['company']
        self.assertEqual(company_data['id'], company.id)
        self.assertEqual(company_data['name'], company.name)
        self.assertEqual(company_data['contact_email'], company.contact_email)
        self.assertEqual(company_data['contact_phone'], company.contact_phone)
        
        # Verify current company ID
        self.assertEqual(self.client.session['current_company_id'], company.id)


class TestLogoutView(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('accounts:logout')
        self.login_url = reverse('accounts:login')
        self.user = UserFactory()

    def test_logout_success(self):
        """Test successful logout"""
        self.client.force_login(self.user)
        self.assertTrue(self._is_logged_in())
        
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertFalse(self._is_logged_in())

    def test_logout_not_logged_in(self):
        """Test logout when not logged in"""
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session