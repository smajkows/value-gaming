from abc import ABC, abstractmethod
from google.cloud import ndb


class BrokerageProfile(object):
    user_id = None
    accounts = []


class NdbBrokerageProfile(BrokerageProfile, ndb.PolyModel):
    platform = ndb.StringProperty(required=True)  # platform

    @classmethod
    def get_user_id(cls, id):
        """
        :param id: id should be the user_id that is returned directly from the platform api for this profile
        :return:
        """
        return '{}_{}'.format(cls.platform, id)


class BrokerageProfileCredentials(object):
    access_token = None
    refresh_token = None
    token_expiration = None
    refresh_expiration = None


class AbstractProfileHandler(ABC):
    MODEL = None
    PLATFORM = None

    @abstractmethod
    def create_profile_from_api(self, profile):
        raise NotImplementedError('YOU MUST IMPLEMENT THIS METHOD CONCRETELY')


