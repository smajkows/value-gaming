from moon_landing_3.accounts.etrade.accounts import EtradeAccountHandler
from moon_landing_3.accounts.td_ameritrade.accounts import TDAmeritradeAccountHandler


class AccountHandlerFactory(object):

    registry = {
        EtradeAccountHandler.PLATFORM: EtradeAccountHandler(),
        TDAmeritradeAccountHandler.PLATFORM: TDAmeritradeAccountHandler()
    }

    @classmethod
    def get_handler(cls, platform):
        try:
            return cls.registry[platform]
        except Exception as e:
            raise Exception("Unable to get handler for platform {} due to {}".format(platform, e))
