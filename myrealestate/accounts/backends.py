from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

# TODO: Use django AllAuth and remove this
class EmailOrUsernameModelBackend(ModelBackend):
    '''
    Allows users to use their email or username. 

    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None