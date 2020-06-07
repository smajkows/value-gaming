from moon_landing_3.accounts.accounts import Account, AbstractAccountHandler, DailyAccountStats, NdbAccount
from google.cloud import ndb, datastore
import datetime

client = datastore.Client()
ndb_client = ndb.Client()


class Etrade(object):
    PLATFORM = 'etrade'


class EtradeAccount(NdbAccount):
    account_id_key = ndb.StringProperty()
    account_name = ndb.StringProperty()  # if this account has a name set by the user for easier identification
    mode = ndb.StringProperty()  # CASH, IRA  etc.
    type = ndb.StringProperty()  # INDIVIDUAL, JOINT etc.
    institution_type = ndb.StringProperty()  # BROKERAGE etc.
    open = ndb.BooleanProperty()  # if the account is still open or not


class EtradeDailyAccountStats(DailyAccountStats, ndb.Model):
    """
    Object to store the daily stats of an account
    """
    account_id = ndb.StringProperty(required=True)  # the id of the etrade account these daily stats are from
    open_balance = ndb.FloatProperty()
    closing_balance = ndb.FloatProperty()
    date = ndb.DateTimeProperty()
    open_cash_balance = ndb.FloatProperty()
    close_cash_balance = ndb.FloatProperty()


class EtradeAccountHandler(Etrade, AbstractAccountHandler):
    MODEL = EtradeAccount
    DAILY_STATS_MODEL = EtradeDailyAccountStats

    def create_account_from_api(self, account):
        with ndb_client.context():
            acct = self.MODEL(id='{}_{}'.format(self.PLATFORM, account['accountId']),
                                       account_id=account['accountId'],
                                       user_id=account['user_id'],
                                       platform=self.PLATFORM)
            acct.account_id_key = account['accountIdKey']
            acct.account_name = account['accountName']
            acct.mode = account['accountMode']
            acct.type = account['accountType']
            acct.institution_type = account['institutionType']
            acct.open = True if account['accountStatus'] != 'CLOSED' else False
            acct.put()
        return acct

    def poll_daily_account_stats(self, account):
        # TODO: implement for Etrade accounts
        return

    def create_daily_stats_from_api(self, account_id, balence_info):
        """
        Given an etrade id and balence info create a daily stats entity
        :param account:
        :return:
        """
        date = datetime.date.today()
        account_id = account_id
        id = '{}_{}'.format(account_id, date)  # TODO: change this into a instance method somehow
        task_key = client.key(self.DAILY_STATS_MODEL.__name__, id)
        stats_object = datastore.Entity(key=task_key)
        return