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
from datetime import datetime, timedelta, timezone
import json
from django.shortcuts import redirect

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
        url = TDAmeritradeAuth().get_login_page()
        return redirect(url)


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


class ReactApp(View):
    template = 'react.html'

    def get(self, request):
        context = {}
        template = loader.get_template(self.template)
        return HttpResponse(template.render(context, request))


class AccountPageHandler(View):
    template = 'account_page.html'

    def get(self, request, account_id):
        template = loader.get_template(self.template)

        query = client.query(kind='NdbDailyAccountStats', order=('date',))
        query = query.add_filter('account', '=', ndb.Key(NdbAccount, account_id)._key)
        daily_stats = query.fetch()

        query2 = client.query(kind='NdbTransaction', order=('-transaction_date',))
        query2 = query2.add_filter('account', '=', ndb.Key(NdbAccount, account_id)._key)
        transactions_fetch = query2.fetch()


        daily_stats_labels = []
        daily_stats_balances = []

        one_week_labels = []
        one_week_balances = []

        one_month_labels = []
        one_month_balances = []

        one_year_labels = []
        one_year_balances = []

        positions = []
        transactions = []

        today = datetime.today()

        for transaction in transactions_fetch:
            if transaction['amount'] and transaction['cost'] <= 0:  # change this heruist should be done when polling
                transactions.append({'instruction': transaction['instruction'],
                                     'type': transaction['type'],
                                     'transaction_date': transaction['transaction_date'],
                                     'symbol': transaction['symbol'],
                                     'amount': transaction['amount'],
                                     'price': transaction['price'],
                                     'cost': transaction['cost']})
        for daily in daily_stats:
            if daily.get('positions'):
                positions = daily.get('positions').decode('utf-8')

            label = daily['date'].strftime("%m/%d/%Y")
            balance = daily['balance']
            daily_date = daily['date'].replace(tzinfo=None)

            if daily_date > today - timedelta(days=7):
                one_week_labels.append(label)
                one_week_balances.append(balance)

            if daily_date > today - timedelta(days=30):
                one_month_labels.append(label)
                one_month_balances.append(balance)

            if daily_date > today - timedelta(days=365):
                one_year_labels.append(label)
                one_year_balances.append(balance)

            daily_stats_labels.append(label)
            daily_stats_balances.append(balance)

        json_positions = json.loads(positions)

        week_gain = (one_week_balances[-1] - one_week_balances[0])/one_week_balances[0] if one_week_balances[0] else 0
        month_gain = (one_month_balances[-1] - one_month_balances[0])/one_month_balances[0] if one_month_balances[0] else 0
        year_gain = (one_year_balances[-1] - one_year_balances[1])/one_year_balances[1]
        alltime_gain = (daily_stats_balances[-1] - daily_stats_balances[1])/daily_stats_balances[1]

        context = {'labels': daily_stats_labels, 'balances': daily_stats_balances, 'positions': json_positions,
                   'transactions': transactions, 'one_week_labels': one_week_labels, 'one_week_balances': one_week_balances,
                   'one_month_labels': one_month_labels, 'one_month_balances': one_month_balances, 'one_year_labels': one_year_labels,
                   'one_year_balances': one_year_balances, 'week_gain': "{:.2%}".format(week_gain), 'month_gain': "{:.2%}".format(month_gain),
                   'year_gain': "{:.2%}".format(year_gain), 'alltime_gain': "{:.2%}".format(alltime_gain)}

        return HttpResponse(template.render(context, request))


class DailyAccountPoll(View):

    def get(self, request):
        accounts_to_poll = NdbAccount.query().fetch()
        for account in accounts_to_poll:
            handler = AccountHandlerFactory.get_handler(account.platform)
            handler.poll_daily_account_stats(account)
        return HttpResponse()