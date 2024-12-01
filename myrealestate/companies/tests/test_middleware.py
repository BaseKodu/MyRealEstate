from django.test import TestCase, RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.http import HttpResponse
from myrealestate.config.middleware import CompanyMiddleware, company_dict
from myrealestate.companies.context_processors import company_context
from myrealestate.accounts.tests.factories import UserFactory
from .factories import CompanyFactory
from ..models import Company
from myrealestate.accounts.models import UserTypeEnums
from django.contrib.auth.models import AnonymousUser

class TestCompanyMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda req: HttpResponse()
        self.middleware = CompanyMiddleware(get_response=self.get_response)
        self.user = UserFactory()
        self.company = CompanyFactory(
            name="Test Company",
            contact_email="company@test.com",
            contact_phone="1234567890"
        )
        self.user.companies.add(
            self.company, 
            through_defaults={'access_level': UserTypeEnums.COMPANY_OWNER}
        )

    def _get_request(self, user=None):
        """Helper to create a request with session and user"""
        request = self.factory.get('/')
        middleware = SessionMiddleware(self.get_response)
        middleware.process_request(request)
        request.session.save()
        
        auth_middleware = AuthenticationMiddleware(self.get_response)
        auth_middleware.process_request(request)
        
        if user:
            request.user = user
        else:
            request.user = self.user
            
        return request

    def test_process_request_sets_company(self):
        """Test middleware sets company in request"""
        request = self._get_request()
        
        # Set initial company data in session
        company_data = company_dict(self.company, self.user)
        request.session['company'] = company_data
        request.session['current_company_id'] = self.company.id
        
        self.middleware.process_request(request)
        self.assertEqual(request.company['id'], self.company.id)
        self.assertEqual(request.company['name'], self.company.name)

    def test_refresh_company_details(self):
        """Test refreshing company details"""
        request = self._get_request()
        request.refresh_company = True
        
        self.middleware.process_request(request)
        
        self.assertIsNotNone(request.company)
        self.assertEqual(request.company['id'], self.company.id)

    def test_no_company_for_user(self):
        """Test handling user with no companies"""
        user_without_company = UserFactory()
        request = self._get_request(user=user_without_company)
        
        self.middleware.process_request(request)
        self.assertIsNone(request.company)


class TestCompanyContextProcessor(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.company = CompanyFactory(
            name="Test Company",
            contact_email="company@test.com",
            contact_phone="1234567890"
        )
        self.user.companies.add(
            self.company, 
            through_defaults={'access_level': UserTypeEnums.COMPANY_OWNER}
        )

    def test_context_processor_authenticated(self):
        """Test context processor with authenticated user"""
        request = RequestFactory().get('/')
        request.user = self.user
        
        # Simulate middleware
        company_data = company_dict(self.company, self.user)
        request.company = company_data
        
        context = company_context(request)
        
        self.assertIsNotNone(context['current_company'])
        self.assertEqual(context['current_company'].id, self.company.id)
        self.assertTrue(len(context['companies']) > 0)

    def test_context_processor_unauthenticated(self):
        """Test context processor with unauthenticated user"""
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        request.company = None
        
        context = company_context(request)
        
        self.assertIsNone(context['current_company'])
        self.assertEqual(len(context['companies']), 0)

    def test_context_processor_invalid_company(self):
        """Test context processor with invalid company in session"""
        request = RequestFactory().get('/')
        request.user = self.user
        
        # Set invalid company data
        invalid_company_data = company_dict(CompanyFactory(), self.user)
        request.company = invalid_company_data
        
        context = company_context(request)
        
        # Should fall back to first available company
        self.assertIsNotNone(context['current_company'])
        self.assertEqual(context['current_company'].id, self.company.id)