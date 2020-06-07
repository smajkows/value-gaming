from moon_landing_3.accounts.accounts import AbstractAccountHandler, NdbDailyAccountStats, NdbAccount
from moon_landing_3.profiles.td_ameritrade.profiles import TDAmeritradeProfile
from td_ameritrade_python_client.client import TDAmeritradeAuth
import datetime
from google.cloud import ndb

ndb_client = ndb.Client()


class TDAmeritrade(object):
    PLATFORM = 'td_ameritrade'


class TDAmeritradeAccount(NdbAccount):
    account_name = ndb.StringProperty()  # if this account has a name set by the user for easier identification
    profile_id = ndb.KeyProperty(required=True)  # the TD ameritrade profile this account belongs to
    mode = ndb.StringProperty()  # CASH, IRA  etc.
    type = ndb.StringProperty()  # INDIVIDUAL, JOINT etc.
    institution_type = ndb.StringProperty()  # BROKERAGE etc.
    acl = ndb.StringProperty()  # acl string
    cd_domain_id = ndb.StringProperty()
    open = ndb.BooleanProperty()  # if the account is still open or not

    def _post_put_hook(self, future):
        profile = self.profile_id.get()
        print(profile)
        if self.key not in profile.accounts:
            profile.accounts.append(self.key)
            profile.put()


class TDAmeritradeDailyAccountStats(NdbDailyAccountStats):
    """
    The ID of this should be the same as the account id it came from, Object to store the daily stats of an account
    """
    pass


class TDAmeritradeAccountHandler(TDAmeritrade, AbstractAccountHandler):
    MODEL = TDAmeritradeAccount
    DAILY_STATS_MODEL = TDAmeritradeDailyAccountStats

    def create_account_from_api(self, account):
        acct = self.MODEL(id='{}_{}'.format(self.PLATFORM, account['accountId']),
                          account_id=account['accountId'],
                          user_id=account['user_id'],
                          platform=self.PLATFORM,
                          profile_id=ndb.Key(TDAmeritradeProfile, account['profile_id']))
        acct.acl = account['acl']
        acct.account_name = account['displayName']
        acct.cd_domain_id = account['accountCdDomainId']
        acct.put()
        return

    def create_accounts_from_api(self, accounts, profile_id, user_id):
        for account in accounts:
            account['user_id'] = user_id  # pass the user_id as part of the account json
            account['profile_id'] = profile_id  # pass the profile (userId) of the TD ameritrade account
            self.create_account_from_api(account)
        return

    def poll_daily_account_stats(self, account):
        profile = account.profile_id.get()
        access_token = profile.access_token
        balance_info = TDAmeritradeAuth().get_account_balances(access_token, account.account_id)
        if not balance_info:
            # crednetials are likely None try to update the user profile
            resp = TDAmeritradeAuth().refresh_token(profile.refresh_token)
            profile.access_token = resp['access_token']
            profile.refresh_token = resp['refresh_token']
            profile.put()
            self.poll_daily_account_stats(account)  # try to repoll this account after updating the profile access token
        self.create_daily_stats_from_api(balance_info)
        account.update_account_balance() # updates the most recent account balance for this account
        return

    def create_daily_stats_from_api(self, balance_info):
        """
        Given an TDAmeritrade id and balence info create a daily stats entity
        :param account:
        :return:
        """

        id = '{}_{}_{}'.format(self.PLATFORM, balance_info['id'], datetime.date.today())
        account_id = '{}_{}'.format(self.PLATFORM, balance_info['id'])

        if ndb.Key(self.MODEL, account_id).get():
            # Only create daily stats for an account if we can find the account it belongs to
            account_key = ndb.Key(self.MODEL, account_id)
            daily_stats = self.DAILY_STATS_MODEL(id=id,
                                                 balance=balance_info['balance'],
                                                 date=datetime.datetime.today(),
                                                 cash_balance=balance_info['cash_balance'],
                                                 account=account_key,
                                                 positions=balance_info['positions'])
            daily_stats.put()
        return
