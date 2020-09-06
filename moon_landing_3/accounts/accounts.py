from google.cloud import ndb
from abc import abstractmethod


class Account(object):
    account_id = None  # the id of the account from the platform
    platform = None  # the platform this account is from ex: etrade, robinhood etc.
    account_id_key = None
    account_name = None  # if this account has a name set by the user for easier identification
    mode = None  # CASH, IRA  etc.
    type = None  # INDIVIDUAL, JOINT etc.
    institution_type = None  # BROKERAGE etc.
    open = None  # if the account is still open or not


class NdbAccessItem(ndb.PolyModel):
    access_token = ndb.StringProperty(required=True)


class NdbAccount(Account, ndb.PolyModel):
    user_id = ndb.StringProperty(required=True)  # firebase user id: that this account was added under
    account_id = ndb.StringProperty(required=True)  # the id of the account from the platform
    platform = ndb.StringProperty(required=True)  # the platform this account was pulled from: plaid, td_ameritrade etc.
    platform_name = ndb.StringProperty()  # the name of the institution: etrade, robinhood etc.
    current_balance = ndb.FloatProperty()  # the most recent balance of this account
    followers = ndb.KeyProperty(repeated=True)  # the keys of NdbUsers who follow this account


class NdbTransaction(ndb.PolyModel):
    account = ndb.KeyProperty(required=True, default=None)  # the account this transaction belongs to
    type = ndb.StringProperty(required=True)  # the type of transaction
    settlement_date = ndb.DateTimeProperty(required=True)
    transaction_date = ndb.DateTimeProperty(required=True)
    transaction_id = ndb.StringProperty(required=True)  # the id of the transaction from the platform api
    description = ndb.StringProperty()
    amount = ndb.FloatProperty()
    price = ndb.FloatProperty()
    cost = ndb.FloatProperty(required=True)
    instruction = ndb.StringProperty()
    symbol = ndb.StringProperty()
    asset_type = ndb.StringProperty()


class DailyAccountStats(object):
    """
    Object to store the daily stats of an account
    """
    open_balance = None
    closing_balance = None
    date = None
    open_cash_balance = None
    close_cash_balance = None


class NdbDailyAccountStats(ndb.PolyModel):
    balance = ndb.FloatProperty(required=True)
    date = ndb.DateTimeProperty(required=True)
    cash_balance = ndb.FloatProperty(required=True)
    account = ndb.KeyProperty(required=True, default=None)
    positions = ndb.JsonProperty()


class AccountHandlerEnum:
    MODEL = 'model'


class AbstractAccountHandler(object):
    """
    This class should never be called directly without a contrete implementation, see EtradeAccountHandler for
    concrete implementation example
    """
    MODEL = 'OVERWRITE ME'
    PLATFORM = 'OVERWRITE ME'
    registry = {PLATFORM: {
        AccountHandlerEnum.MODEL: MODEL
        }
    }

    @classmethod
    def get_handler(cls, platform):
        try:
            return cls.registry[platform][AccountHandlerEnum.MODEL]
        except Exception as e:
            raise Exception("Can not get model cls for platform: {} from {} due to {}".
                            format(platform, cls.__name__, e))

    @abstractmethod
    def poll_daily_account_stats(self, account):
        raise NotImplementedError('THIS METHOD MUST BE IMPLEMENTED CONCRETELY')
