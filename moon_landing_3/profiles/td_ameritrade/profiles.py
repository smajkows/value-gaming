from moon_landing_3.profiles.profiles import BrokerageProfileCredentials
from moon_landing_3.profiles.profiles import AbstractProfileHandler, NdbBrokerageProfile
from google.cloud import ndb


class TDAmeritradeProfile(NdbBrokerageProfile):
    access_token = ndb.StringProperty(required=True)
    refresh_token = ndb.StringProperty()
    accounts = ndb.KeyProperty(repeated=True)


class TDAmeritradeProfileHandler(AbstractProfileHandler):
    MODEL = TDAmeritradeProfile
    PLATFORM = 'td_ameritrade'

    def create_profile_from_api(self, profile):
        id = profile['userId']
        profile = self.MODEL(id=id,
                             platform=self.PLATFORM,
                             access_token=profile['resp']['access_token'],
                             refresh_token=profile['resp']['refresh_token'])
        profile.put()
        return
