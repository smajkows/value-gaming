from moon_landing_3.profiles.td_ameritrade.profiles import TDAmeritradeProfileHandler


class ProfileHandlerFactory(object):

    registry = {
        TDAmeritradeProfileHandler.PLATFORM: TDAmeritradeProfileHandler()
    }

    @classmethod
    def get_handler(cls, platform):
        try:
            return cls.registry[platform]
        except Exception as e:
            raise Exception("Unable to get handler for platform {} due to {}".format(platform, e))