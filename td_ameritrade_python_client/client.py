from rauth import OAuth2Service
from td_ameritrade_python_client.config_file import CONSUMER_KEY
import requests
import webbrowser
import json
import urllib.parse
import os
from env_variables import DEV_APP_ID
import logging


def is_dev_environment():
    """ Return true if running on a local dev environment, false otherwise """
    return os.getenv('APPLICATION_ID', None) == DEV_APP_ID


if is_dev_environment():
    base_url = 'http://localhost:8000'
else:
    base_url = 'http://project-moon-landing.appspot.com'


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
        #webbrowser.open(url)
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

    def get_account_balances(self, access_token, account_id, positions=True):
        url = 'https://api.tdameritrade.com/v1/accounts/{}'.format(account_id)
        if positions:
            url += '?fields=positions'
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        response = requests.get(url, headers=headers).json()
        if response.get('error'):
            print('error in getting user_info')
            return None
        print(response)
        balance_info = {
            'id': response['securitiesAccount']['accountId'],
            'balance': response['securitiesAccount']['initialBalances']['accountValue'],
            'cash_balance': response['securitiesAccount']['initialBalances']['cashBalance'],
            'positions': response['securitiesAccount'].get('positions')
        }
        print(balance_info['positions'])
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



