from django.http import HttpResponse
from django.template import loader
from etrade_python_client.etrade_python_client import OauthTextInputHandler
from td_ameritrade_python_client.client import TDAmeritradeAuth
from moon_landing_3.accounts.utility import AccountHandlerFactory
from moon_landing_3.accounts.accounts import NdbAccount
from moon_landing_3.profiles.utility import ProfileHandlerFactory
from django.views import View
from google.auth.transport import requests
from google.cloud import datastore, ndb
from django.core.exceptions import PermissionDenied
import google.oauth2.id_token
from datetime import datetime
import json

firebase_request_adapter = requests.Request()
client = datastore.Client()


# TODO: protect this handler by login required
class HomePageHandler(View):
    template = 'profile.html'

    def get(self, request):
        profiles = []
        id_token = request.COOKIES.get('token')  # TODO: for some reason the token isn't getting set on the sign in check base.html javascript
        # TODO: refactor user check into a decorator
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                query = client.query(kind='NdbAccount')
                query = query.add_filter('user_id', '=', claims['user_id'])
                profiles = query.fetch()
            except ValueError as exc:
                error_message = str(exc)
            template = loader.get_template(self.template)
            context = {'user_info': profiles}
            return HttpResponse(template.render(context, request))

        raise PermissionDenied  # If we don't have a user return a 403 error


# TODO: protect this handler by login required
class LeaderboardPageHandler(View):
    template = 'leaderboard.html'

    def get(self, request):
        profiles = []
        id_token = request.COOKIES.get('token')  # TODO: for some reason the token isn't getting set on the sign in check base.html javascript
        # TODO: refactor user check into a decorator
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                query = client.query(kind='NdbAccount', order=('current_balance',))  # This will need to be ordered and adjusted based on the value/gain
                profiles = query.fetch()
            except ValueError as exc:
                error_message = str(exc)
            template = loader.get_template(self.template)
            context = {'profiles': profiles}
            return HttpResponse(template.render(context, request))

        raise PermissionDenied  # If we don't have a user return a 403 error


def landing(request):
    template = loader.get_template('base.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    template = loader.get_template('login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def datastore_test_page(request):
    template = loader.get_template('datastore-test.html')
    items = client.query(kind='NdbAccount').fetch()
    daily_account_stats = client.query(kind='NdbDailyAccountStats').fetch()
    positions = []
    for account_stat in daily_account_stats:
        print(account_stat.get('balance'))
        if account_stat.get('positions'):
            positions = account_stat.get('positions').decode('utf-8')
    print(positions)
    json_positions = json.loads(positions)
    print(type(json_positions))
    context = {'items': items, 'daily_account_stats': json_positions}
    return HttpResponse(template.render(context, request))


auth_handler = OauthTextInputHandler()


class AuthHandler(View):

    @classmethod
    def get(cls, request, platform):
        cls.template = loader.get_template('{}_login.html'.format(platform))
        handler = AuthHandlerFactory.registry[platform]
        return handler.get(request, platform)


class EtradeAuthHandler(AuthHandler):
    def get(self, request, platform):
        auth_handler.oauth_text_input()
        context = {'platform': str(platform)}
        return HttpResponse(self.template.render(context, request))


class TDAmeritradeAuthHandler(AuthHandler):
    def get(self, request, platform):
        TDAmeritradeAuth().get_login_page()
        return HttpResponse()


class AuthHandlerFactory(View):
    registry = {
        'etrade': EtradeAuthHandler(),
        'td-ameritrade': TDAmeritradeAuthHandler()
    }


class AuthCallbackHandler(View):
    def get(self, request, platform):
        callback_handler = AuthCallbackFactory.registry[platform]
        return callback_handler.get(request, platform)


class TDAmeritradeCallbackHandler(AuthCallbackHandler):
    template = HomePageHandler.template

    def get(self, request, platform):
        print("Callback ,TD ameritrade handler")
        code = request.GET.get('code')
        template = loader.get_template(self.template)
        user_info = {}
        if code:
            resp = TDAmeritradeAuth().get_token(code)
            access_token = resp['access_token']
            refresh_token = resp['refresh_token']
            # date = datetime.datetime.now()
            # expires_at = date + datetime.timedelta(resp['expires_in'])
            # refresh_expire = date + datetime.timedelta(resp['refresh_token_expires_in'])
            user_info = TDAmeritradeAuth().get_user_info(access_token, refresh_token)
            user_info['resp'] = resp
            profile_handler = ProfileHandlerFactory.get_handler('td_ameritrade')
            profile_handler.create_profile_from_api(user_info)
            account_handler = AccountHandlerFactory.get_handler('td_ameritrade')
            # TODO: refactor user check into a decorator
            id_token = request.COOKIES.get('token')  # None #  request.get("token")
            if id_token:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                account_handler.create_accounts_from_api(user_info['accounts'], user_info['userId'], claims['user_id'])

        return HomePageHandler().get(request)


class EtradeAuthTextHandler(AuthCallbackHandler):

    def get(self, request, platform):
        PLATFORM = platform
        text_code = request.GET.get('text_code', None)
        session, base_url = auth_handler.oauth_text_input_receiver(text_code)
        template = loader.get_template('ranking_page.html')

        # TODO: move this into a queued task #
        # Gets accounts for this etrade Profile
        # Creates these accounts
        id_token = request.COOKIES.get('token')  # None #  request.get("token")
        if id_token:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            account_list = auth_handler.get_account_list()
            for account in account_list:
                handler = AccountHandlerFactory.get_handler(PLATFORM)
                account['user_id'] = claims['user_id']
                acc_obj = handler.create_account_from_api(account)  # creates account from the api response
                auth_handler.get_balance_info(account['accountIdKey'])
            # END TODO #
        return HomePageHandler().get(request)


class AuthCallbackFactory(View):
    registry = {
        'etrade': EtradeAuthTextHandler(),
        'amtrade': TDAmeritradeCallbackHandler()
    }


class AccountPageHandler(View):
    template = 'account_page.html'

    def get(self, request, account_id):
        template = loader.get_template(self.template)
        query = client.query(kind='NdbDailyAccountStats', order=('date',))
        query = query.add_filter('account', '=', ndb.Key(NdbAccount, account_id)._key)
        daily_stats = query.fetch()
        daily_stats_data = []
        positions = []
        for daily in daily_stats:
            if daily.get('positions'):
                positions = daily.get('positions').decode('utf-8')
            daily_stats_data.append({'x': daily['date'].strftime("%m/%d/%Y"), 'y': daily['balance']})
        json_positions = json.loads(positions)
        context = {'balance_stats': daily_stats_data, 'positions': json_positions}
        return HttpResponse(template.render(context, request))


class DailyAccountPoll(View):

    def get(self, request):
        accounts_to_poll = NdbAccount.query().fetch()
        for account in accounts_to_poll:
            print(account)
            handler = AccountHandlerFactory.get_handler(account.platform)
            handler.poll_daily_account_stats(account)
        return HttpResponse()