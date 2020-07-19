from td_ameritrade_python_client.config_file import CONSUMER_KEY, CONSUMER_KEY_LOCAL
import requests
import urllib.parse
import os
from env_variables import DEV_APP_ID
import logging


def is_dev_environment():
    """ Return true if running on a local dev environment, false otherwise """
    return os.getenv('APPLICATION_ID', None) == DEV_APP_ID


if is_dev_environment():
    base_url = 'http://localhost:8000'
    CONSUMER_KEY = CONSUMER_KEY_LOCAL
else:
    base_url = 'http://project-moon-landing.appspot.com'

print(base_url)


class TDAmeritradeAuth(object):
    def __init__(self):
        self.redirect_uri = base_url + '/callback/amtrade'
        self.client_id = CONSUMER_KEY
        self.authorize_url = 'http://auth.tdameritrade.com/auth'

    def get_login_page(self):
        url = self.authorize_url + '?response_type=code' + '&redirect_uri=' + \
              urllib.parse.quote('{}'.format(self.redirect_uri), safe='') + '&client_id=' + \
              self.client_id + '%40AMER.OAUTHAP'
        logging.debug("URL {} for TDAmeritradeAuth".format(url))
        return url

    def get_token(self, code):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'authorization_code',
            'refresh_token': '',
            'access_type': 'offline',
            'code': code,
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        response = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data).json()
        return response


    def get_account_transactions(self, access_token, account_id):

        url = 'https://api.tdameritrade.com/v1/accounts/{}/transactions'.format(account_id)

        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }

        transaction_list = requests.get(url, headers=headers).json()
        transaction_object = {'account_id': account_id, 'transactions': transaction_list}
        return transaction_object


    def get_account_balances(self, access_token, account_id, positions=True):
        url = 'https://api.tdameritrade.com/v1/accounts/{}'.format(account_id)
        if positions:
            url += '?fields=positions'
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        response = requests.get(url, headers=headers).json()
        if response.get('error'):
            print('error in getting account balances')
            print(response.get('error'))
            return None
        balance_info = {
            'id': response['securitiesAccount']['accountId'],
            'balance': response['securitiesAccount']['currentBalances']['liquidationValue'],
            'cash_balance': response['securitiesAccount']['currentBalances']['availableFunds'],
            'positions': response['securitiesAccount'].get('positions')
        }
        return balance_info

    def get_user_info(self, access_token, refresh_token):
        url = 'https://api.tdameritrade.com/v1/userprincipals'

        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }

        response = requests.get(url, headers=headers).json()
        if response.get('error'):
            print('error in getting user_info')
            refresh_token_response = self.refresh_token(refresh_token)
            access_token = refresh_token_response['access_token']
            refresh_token = refresh_token_response['refresh_token']
            self.get_user_info(access_token, refresh_token)
        return response

    def refresh_token(self, refresh_token):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'access_type': 'offline',
            'code': '',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        print('refreshing token with : {}'.format(refresh_token))
        response = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data).json()
        return response



