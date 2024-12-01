import factory
from django.contrib.auth import get_user_model
from ..models import UserCompanyAccess, UserTypeEnums

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'username{n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True

