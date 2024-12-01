from myrealestate.companies.models import Company
import factory

class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'Company {n}')
    contact_email = factory.Sequence(lambda n: f'company{n}@example.com')
    contact_phone = factory.Sequence(lambda n: f'+1234567890{n}')