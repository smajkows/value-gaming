from moon_landing_3.accounts.etrade.accounts import EtradeAccountHandler
from moon_landing_3.accounts.td_ameritrade.accounts import TDAmeritradeAccountHandler
from moon_landing_3.accounts.plaid.accounts import PlaidAccountHandler


class AccountHandlerFactory(object):

    registry = {
        EtradeAccountHandler.PLATFORM: EtradeAccountHandler(),
        TDAmeritradeAccountHandler.PLATFORM: TDAmeritradeAccountHandler(),
        PlaidAccountHandler.PLATFORM: PlaidAccountHandler()
    }

    @classmethod
    def get_handler(cls, platform):
        try:
            handler = cls.registry[platform]
            return handler
        except Exception as e:
            return None
