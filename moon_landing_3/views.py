from django.http import HttpResponse
from django.template import loader
from etrade_python_client.etrade_python_client import OauthTextInputHandler
from td_ameritrade_python_client.client import TDAmeritradeAuth
from moon_landing_3.accounts.utility import AccountHandlerFactory
from moon_landing_3.accounts.accounts import NdbAccount, NdbDailyAccountStats, NdbTransaction
from moon_landing_3.profiles.utility import ProfileHandlerFactory
from moon_landing_3.accounts.plaid.accounts import PlaidAccount, PlaidItem
from moon_landing_3.user import NdbUser, NdbBraintreePlan, NdbBraintreeSubscription
from django.views import View
from google.auth.transport import requests
from google.cloud import datastore, ndb
from django.core.exceptions import PermissionDenied
import google.oauth2.id_token
from datetime import datetime, timedelta
import json
from django.shortcuts import redirect
from moon_landing_3.utilities import plaid_client
from utils import get_braintree_url

import requests as rq

firebase_request_adapter = requests.Request()
client = datastore.Client()


class PlaidAccountCreation(View):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if not body.get('is_update', None):
            response = plaid_client.Item.public_token.exchange(body['token']) # use plaid client to get perm access token
            access_token = response['access_token']  #this access token shouldn't expire
            item_id = response['item_id']  # the item_id for the access token
        else:
            item_id = body.get('item_id')
            access_token = ndb.Key(PlaidItem, item_id).get().access_token
        account_handler = AccountHandlerFactory.get_handler('plaid')
        # TODO: refactor user check into a decorator
        id_token = request.COOKIES.get('token')  # None #  request.get("token")
        if id_token:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            account_handler.create_accounts_from_api(body, item_id, claims['user_id'], access_token)
        return HttpResponse()


class PlaidToken(View):
    def get(self, request):
        id_token = request.COOKIES.get('token')
        item_id = request.GET.get('item_id', None)
        if id_token:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            input_dict = {
                    'user': {
                        'client_user_id': claims['user_id'],
                    },
                    'client_name': "Moon Landing",
                    'products': ['investments', 'transactions'],
                    'country_codes': ['US'],
                    'language': "en",
                }
            if item_id and item_id != 'undefined':
                input_dict['access_token'] = ndb.Key(PlaidItem, item_id).get().access_token
                input_dict.pop('products')

            response = plaid_client.LinkToken.create(input_dict)
            return HttpResponse(json.dumps(response['link_token']))
        raise PermissionDenied


class FollowAccountHandler(View):

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        target_account_id = body['target_account_id']
        follow_action = body['follow_action']
        id_token = body['firebase_token']
        context = {}
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
                if not moon_landing_user:
                    return HttpResponse(400)
                target_account = ndb.Key(NdbAccount, target_account_id).get()
                if not target_account:
                    return HttpResponse(400)

                if follow_action == 'unfollow':
                    moon_landing_user.followed_accounts.remove(target_account.key)
                    target_account.followers.remove(moon_landing_user.key)
                if follow_action == 'follow':
                    free_plan = ndb.Key(NdbBraintreePlan, 'free_plan').get()
                    user_limit = free_plan.followers_allowed  # set the user default limit to 1
                    users_sub = moon_landing_user.subscription.get()
                    if users_sub:
                        user_limit = users_sub.plan.get().followers_allowed
                    if len(moon_landing_user.followed_accounts) < user_limit:
                        moon_landing_user.followed_accounts.append(target_account.key)
                        target_account.followers.append(moon_landing_user.key)
                    else:
                        context['error'] = 'Upgrade your plan in Settings to follow more accounts!'
                        return HttpResponse(json.dumps(context))

                    # if the user is over the limit we should prompt the frontend saying that they need to upgrade
                    # to follow more accounts

                moon_landing_user.followed_accounts = list(set(moon_landing_user.followed_accounts))
                moon_landing_user.put()
                target_account.followers = list(set(target_account.followers))
                target_account.put()
                context = {'follow_status': target_account.key in moon_landing_user.followed_accounts,
                           'follower_count': len(target_account.followers)}
            except:
                return HttpResponse(400)
        return HttpResponse(json.dumps(context))


class BraintreeToken(View):
    def get(self, request):
        braintree_service_base_url = get_braintree_url()
        id_token = request.COOKIES.get('token')
        claims = google.oauth2.id_token.verify_firebase_token(
            id_token, firebase_request_adapter)
        user_id = claims.get('user_id', None)
        try:
            response = rq.get(braintree_service_base_url + '/braintree_client_token',
                                    params={'user_id': user_id,
                                            'email': claims.get('email', None)})
            client_token = response.json()
        except Exception as e:
            print('Problem requesting Braintree client token, payment section will not load without this.'
                            'exception: {}'.format(e))
            client_token = ''  # set an empty client token
        return HttpResponse(json.dumps(client_token))


class BraintreePaymentMethod(View):
    def post(self, request):
        braintree_service_base_url = get_braintree_url()
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        id_token = body['firebase_token']
        payment_nonce = body['payment_nonce']
        claims = google.oauth2.id_token.verify_firebase_token(
        id_token, firebase_request_adapter)
        response = rq.post(braintree_service_base_url + '/add_payment_method',
                           data={'user_id': claims.get('user_id', None),
                                 'email': claims.get('email', None),
                                 'payment_nonce': payment_nonce})
        return


class BraintreePlanHanlder(View):
    def get(self, request):
        braintree_service_base_url = get_braintree_url()
        plans = rq.get(braintree_service_base_url + '/get_plans')
        json_plans = plans.json()
        for plan_id in json_plans:
            plan = json_plans[plan_id]
            print(plan)
            moon_landing_plan = NdbBraintreePlan(id=plan['id'], name = plan['name'],
                                                 braintree_id=plan['id'], description=plan['description'],
                                                 price=float(plan['price']), created_at=datetime.strptime(plan['created_at'], '%d/%m/%Y'))
            moon_landing_plan.put()
            print(moon_landing_plan)
        return HttpResponse()


class Settings(View):
    template = 'react.html'

    def get(self, request):
        id_token = request.COOKIES.get('token')  # TODO: for some reason the token isn't getting set on the sign in check base.html javascript
        # TODO: refactor user check into a decorator
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
            except ValueError as exc:
                error_message = str(exc)
            template = loader.get_template(self.template)
            context = {}
            return HttpResponse(template.render(context, request))

        raise PermissionDenied  # If we don't have a user return a 403 error


class SettingsJson(View):
    def get(self, request):
        id_token = request.COOKIES.get('token')
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
                sub_id = None
                if moon_landing_user.subscription:
                    sub_id = moon_landing_user.subscription.id()
                available_plans = NdbBraintreePlan.query().fetch()
                user_current_plan = moon_landing_user.braintree_plan.get()
                current_plan_json = {'id': user_current_plan.braintree_id, 'description': user_current_plan.description, 'price':
                                     user_current_plan.price, 'followers_allowed': user_current_plan.followers_allowed,
                                     'name': user_current_plan.name }
                available_plans_list = []
                for plan in available_plans:
                    available_plans_list.append({
                        'id': plan.braintree_id,
                        'description': plan.description,
                        'price': plan.price,
                        'followers_allowed': plan.followers_allowed,
                        'name': plan.name
                    })

            except ValueError as exc:
                error_message = str(exc)
            context = {'available_plans': available_plans_list, 'current_plan': current_plan_json, 'subscription': sub_id}
            return HttpResponse(json.dumps(context))


class HandlePlanUpgrade(View):
    def post(self, request):
        braintree_service_base_url = get_braintree_url()
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        id_token = body['firebase_token']
        plan_id = body['plan_id']
        context = {}
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
                if not moon_landing_user.braintree_plan:
                    moon_landing_user.braintree_plan = ndb.Key(NdbBraintreePlan, 'free_plan') # set to free plan by default
                current_plan = moon_landing_user.braintree_plan.get()
                print('current plan {}'.format(current_plan))
                sub_id = None
                print(moon_landing_user.subscription)
                if moon_landing_user.subscription:
                    sub_id = moon_landing_user.subscription.id()
                    print(sub_id)

                result = rq.post(braintree_service_base_url + '/update_user_plan', data={'user_id': claims['user_id'],
                                                                                         'plan_id': plan_id,
                                                                                         'subscription_id': sub_id })
                json_result = result.json()
                print(json_result)
                if json_result['success']:
                    print('json success {}'.format(json_result))
                    sub = NdbBraintreeSubscription(id=json_result['subscription_id'],
                                                   plan=ndb.Key(NdbBraintreePlan, plan_id),
                                                   subscription_id=json_result['subscription_id'],
                                                   user=ndb.Key(NdbUser, claims['user_id']))
                    print('sub {}'.format(sub))
                    sub.put()
                    print(sub)
                    moon_landing_user.braintree_plan = ndb.Key(NdbBraintreePlan, plan_id)
                    moon_landing_user.subscription = sub.key
                    moon_landing_user.put()
                    print('checking sub status')
                    moon_landing_user.check_subscription_status()
                print("braintree plan {}".format(moon_landing_user.braintree_plan))
                current_plan = moon_landing_user.braintree_plan.get()
                print("currrent plan after json_result {}".format(current_plan))
                current_plan_json = {'id': current_plan.braintree_id, 'description': current_plan.description, 'price':
                                     current_plan.price, 'name': current_plan.name}
                context['current_user_plan'] = current_plan_json
                context['subscription'] = sub_id
            except Exception as e:
                print(e)

        return HttpResponse(json.dumps(context))



class FollowedTransactionsJson(View):

    def get(self, request):
        followed_transactions = []
        id_token = request.COOKIES.get('token')
        if id_token:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
            today_minus_delta = datetime.today() - timedelta(days=5)
            for followed_account_key in moon_landing_user.followed_accounts:
                # for each followed account get its latest transactions
                transactions = NdbTransaction.query(NdbTransaction.account == followed_account_key,
                                                    NdbTransaction.settlement_date > today_minus_delta)
                account = followed_account_key.get()
                display_name = account.account_screen_name if account.account_screen_name else account.account_name
                for transaction in transactions:
                    followed_transactions.append({'instruction': transaction.instruction,
                                         'type': transaction.type,
                                         'account_name': display_name,
                                         'transaction_date': transaction.transaction_date.strftime("%m/%d/%Y"),
                                         'symbol': transaction.symbol,
                                         'amount': transaction.amount,
                                         'price': transaction.price,
                                         'cost': transaction.cost})
            sorted_transactions = sorted(followed_transactions, key=lambda i: i['transaction_date'], reverse=True)
        context = {'followed_transactions': sorted_transactions}
        return HttpResponse(json.dumps(context))


class HomePageJson(View):

    def get(self, request):
        accounts_list = []
        id_token = request.COOKIES.get('token')
        if id_token:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
            accounts = NdbAccount.query(NdbAccount.user_id == claims['user_id']).fetch()
            account_keys = []
            followed_accounts = []
            followers = []
            need_put = False
            for account in accounts:
                item_id = ''
                if not account.plaid_valid:
                    item_id = account.plaid_item_entity.id()
                account_keys.append(account.key)
                accounts_list.append({'platform': account.platform, 'account_name': account.account_name,
                                      'balance': account.current_balance, 'plaid_valid': account.plaid_valid,
                                      'item_id': item_id})
                followers.extend(account.followers)

            for account in moon_landing_user.followed_accounts:
                full_account = account.get()
                if full_account:
                    followed_accounts.append({'account_name': full_account.account_screen_name,
                                              'balance': full_account.current_balance})
                else:
                    moon_landing_user.followed_accounts.remove(account)
                    account.followers.remove(moon_landing_user.key)
                    account.put()
                    need_put = True
            if not moon_landing_user:
                moon_landing_user = NdbUser(id=claims['user_id'], firebase_id=claims['user_id'],
                                            linked_accounts=[account for account in account_keys])
            if need_put:
                moon_landing_user.put()

        context = {'accounts': accounts_list, 'username': moon_landing_user.screen_name,
                   'followedaccounts': followed_accounts, 'unique_followers': len(list(set(followers)))}
        return HttpResponse(json.dumps(context))


# TODO: protect this handler by login required
class HomePageHandler(View):
    template = 'react.html'

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


class ChangeUsername(View):

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        requested_username = body['username']
        id_token = body['firebase_token']
        context = {}
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
                moon_landing_user.screen_name = requested_username  # update their username
                moon_landing_user.put()
                context = {'username': moon_landing_user.screen_name}
            except:
                return HttpResponse(400)
        return HttpResponse(json.dumps(context))


class PlaidTransactionWebhook(View):

    def post(self, request):

        # TODO: validate header, stop process if its not valid
        """
        header_unicode = request.header.decode('utf-8')
        header = json.loads(header_unicode)
        resp = plaid_client.Webhooks.get_verification_key(header.get('kid'))


        if request.POST.get('webhook_type') != 'TRANSACTIONS':
            # return 400 not the right type of webhook for this handler
            return HttpResponse(400)

        """
        item_id = request.POST.get('item_id')
        if not item_id:
            # Need item id to continue
            return HttpResponse(400)

        item = ndb.Key(PlaidItem, item_id).get()

        if not item:
            # we don't have a matching item for this in the system terminate here
            return HttpResponse(400)

        # Get all ndb accounts that are linked to this plaid item_id
        accounts = PlaidAccount.query(PlaidAccount.plaid_item_entity == ndb.Key(PlaidItem, item_id)).fetch()
        for account in accounts:
            handler = AccountHandlerFactory.get_handler(account.platform)
            if handler:
                handler.poll_daily_account_stats(account)

        return HttpResponse()


# TODO: protect this handler by login required
class LeaderboardPageHandler(View):
    template = 'react.html'

    def get(self, request):
        profiles = []
        id_token = request.COOKIES.get('token')  # TODO: for some reason the token isn't getting set on the sign in check base.html javascript
        # TODO: refactor user check into a decorator
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                query = client.query(kind='NdbAccount', order=('-current_balance',))  # This will need to be ordered and adjusted based on the value/gain
                profiles = query.fetch()
            except ValueError as exc:
                error_message = str(exc)
            template = loader.get_template(self.template)
            context = {'profiles': profiles}
            return HttpResponse(template.render(context, request))

        raise PermissionDenied  # If we don't have a user return a 403 error


class LeaderboardPageHandler2(View):

    def get(self, request):
        # TODO: return 403 message to non-users , id_token = request.COOKIES.get('token')
        profiles_json = []
        id_token = request.COOKIES.get('token')  # TODO: for some reason the token isn't getting set on the sign in check base.html javascript
        year_ago = datetime.today() - timedelta(days=365)
        if id_token:
            query = NdbAccount.query().order(-NdbAccount.current_balance)  # adjust based on gain/loss
            accounts = query.fetch()
            for account in accounts:
                query = NdbDailyAccountStats.query(NdbDailyAccountStats.account == account.key,
                                                   NdbDailyAccountStats.date > year_ago)\
                    .order(NdbDailyAccountStats.date)
                account_values = query.fetch()
                ytd = (account_values[-1].balance - account_values[0].balance) / account_values[0].balance
                screen_name = account.account_screen_name
                if account.platform == 'plaid':
                    moon_landing_user = ndb.Key(NdbUser, account.user_id).get()
                    if moon_landing_user:
                        screen_name = moon_landing_user.screen_name
                        if account.account_screen_name != screen_name:
                            account.account_screen_name = screen_name
                            account.put()
                display_name = screen_name if screen_name else account.account_name
                profiles_json.append({'platform': account.platform, 'account_id': account.account_id,
                                      'display_name': display_name, 'value': account.current_balance,
                                      'link': '/account/page/' + account.platform + '_' + account.account_id,
                                      'platform_name': account.platform_name, 'follower_count': len(account.followers),
                                      'ytd': ytd})
            return HttpResponse(json.dumps(profiles_json))

        raise PermissionDenied


def landing(request):
    template = loader.get_template('react.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    template = loader.get_template('react.html')
    context = {}
    return HttpResponse(template.render(context, request))


def datastore_test_page(request):
    template = loader.get_template('datastore-test.html')
    context = {'items': []}
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


class AccountDataHandler(View):

    def get(self, request, account_id):

        id_token = request.COOKIES.get('token')  #TODO switch from cookies to session
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                moon_landing_user = NdbUser.query(NdbUser.firebase_id == claims['user_id']).get()
            except:
                return HttpResponse(400)

        if ndb.Key(NdbAccount, account_id)._key not in moon_landing_user.followed_accounts:
            teaser = True

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
            if not teaser:
                transactions.append({'instruction': transaction['instruction'],
                                     'type': transaction['type'],
                                     'transaction_date': transaction['transaction_date'].strftime("%m/%d/%Y"),
                                     'symbol': transaction['symbol'],
                                     'amount': transaction['amount'],
                                     'price': transaction['price'],
                                     'cost': transaction['cost']})
        daily_data_chart = []

        for daily in daily_stats:
            if daily.get('positions'):
                positions = daily.get('positions').decode('utf-8')

            label = daily['date'].strftime("%m/%d/%Y")
            balance = daily['balance']
            daily_date = daily['date'].replace(tzinfo=None)

            if daily_date > today - timedelta(days=7):
                one_week_labels.append(label)
                one_week_balances.append(balance)
                daily_data_chart.append({'time': label, 'amount': balance})

            if daily_date > today - timedelta(days=30):
                one_month_labels.append(label)
                one_month_balances.append(balance)

            if daily_date > today - timedelta(days=365):
                one_year_labels.append(label)
                one_year_balances.append(balance)

            daily_stats_labels.append(label)
            daily_stats_balances.append(balance)

        json_positions = json.loads(positions)
        account = ndb.Key(NdbAccount, account_id).get()

        follow_status = True if account.key in moon_landing_user.followed_accounts else False

        try:
            week_gain = (one_week_balances[-1] - one_week_balances[0])/one_week_balances[0] if one_week_balances[0] else 0
        except:
            week_gain = 0

        try:
            month_gain = (one_month_balances[-1] - one_month_balances[0])/one_month_balances[0] if one_month_balances[0] else 0
        except:
            month_gain = 0

        try:
            year_gain = (one_year_balances[-1] - one_year_balances[0])/one_year_balances[0]
        except:
            year_gain = 0

        try:
            alltime_gain = (daily_stats_balances[-1] - daily_stats_balances[0])/daily_stats_balances[0]
        except:
            alltime_gain = 0

        context = {'labels': daily_stats_labels, 'balances': daily_stats_balances, 'positions': json_positions,
                   'account_name': account.account_screen_name, 'followers': len(account.followers),
                   'follow_status': follow_status, 'account_id': account_id, 'current_balance': account.current_balance,
                   'transactions': transactions, 'one_week_labels': one_week_labels, 'one_week_balances': one_week_balances,
                   'one_month_labels': one_month_labels, 'one_month_balances': one_month_balances, 'one_year_labels': one_year_labels,
                   'one_year_balances': one_year_balances, 'week_gain': "{:.2%}".format(week_gain), 'month_gain': "{:.2%}".format(month_gain),
                   'year_gain': "{:.2%}".format(year_gain), 'alltime_gain': "{:.2%}".format(alltime_gain), 'daily_data_chart': daily_data_chart,
                   'teaser': teaser}

        return HttpResponse(json.dumps(context))


class AccountPageHandler(View):
    template = 'react.html'

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

        try:
            week_gain = (one_week_balances[-1] - one_week_balances[0])/one_week_balances[0] if one_week_balances[0] else 0
        except:
            week_gain = 0

        try:
            month_gain = (one_month_balances[-1] - one_month_balances[0])/one_month_balances[0] if one_month_balances[0] else 0
        except:
            month_gain = 0

        try:
            year_gain = (one_year_balances[-1] - one_year_balances[0])/one_year_balances[0]
        except:
            year_gain = 0

        try:
            alltime_gain = (daily_stats_balances[-1] - daily_stats_balances[0])/daily_stats_balances[0]
        except:
            alltime_gain = 0


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
            if handler:
                handler.poll_daily_account_stats(account)
        return HttpResponse()