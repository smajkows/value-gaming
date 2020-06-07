from django.db import models


class User(object):
    """
    A user in our system
    """
    accounts = []
    profiles = []


class UserProfile(object):
    """
    User accounts associated with trading platforms like an etrade or Robinhood sign in
    """
    type = None  # The trading platform name
    accounts = []  # The accounts associated with this profile


class MoonLandingUser(User):
    pass


class DjangoMoonLandingUser(models.Model, MoonLandingUser):
    pass

