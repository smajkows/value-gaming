"""This Python script provides examples on using the E*TRADE API endpoints"""
from __future__ import print_function
import webbrowser

import configparser
from rauth import OAuth1Service
from etrade_python_client.accounts.accounts import Accounts
from etrade_python_client.market.market import Market
from etrade_python_client.config_file import CONSUMER_KEY, CONSUMER_SECRET, PROD_BASE_URL, SANDBOX_BASE_URL

# loading configuration file
config = configparser.ConfigParser()
config.read('config.ini')




class OauthTextInputHandler(object):
    def __init__(self):
        self.etrade = OAuth1Service(
            name="etrade",
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com")
        self.request_token = None
        self.request_token_secret = None
        self.base_url = SANDBOX_BASE_URL
        self.session = None

    def oauth_text_input(self, sandbox=True):
        if not sandbox:
            self.base_url = PROD_BASE_URL

        # Step 1: Get OAuth 1 request token and secret
        self.request_token, self.request_token_secret = self.etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Go through the authentication flow. Login to E*TRADE.
        # After you login, the page will provide a text code to enter.
        authorize_url = self.etrade.authorize_url.format(self.etrade.consumer_key, self.request_token)
        webbrowser.open(authorize_url)
        return

    def oauth_text_input_receiver(self, text_code):
        # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
        self.session = self.etrade.get_auth_session(self.request_token,
                                                    self.request_token_secret, params={"oauth_verifier": text_code})
        return self.session, self.base_url

    def get_account_list(self):
        accounts = Accounts(self.session, self.base_url)
        account_list = accounts.get_account_list()
        return account_list

    def get_transactions_list(self, account_key_id):
        accounts = Accounts(self.session, self.base_url)
        transactions_list = accounts.get_transactions_list(account_key_id)
        return transactions_list

    def get_orders_list(self, account_key_id):
        accounts = Accounts(self.session, self.base_url)
        get_orders_list = accounts.get_order_list(account_key_id)
        return get_orders_list

    def get_balance_info(self, account_key_id):
        accounts = Accounts(self.session, self.base_url)
        balance_info = accounts.get_balance_info(account_key_id)
        return balance_info


def get_account_list(session, base_url):
    accounts = Accounts(session, base_url)
    account_list = accounts.get_account_list()
    return account_list


def original_oauth():
    """Allows user authorization for the sample application with OAuth 1"""
    etrade = OAuth1Service(
        name="etrade",
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url="https://api.etrade.com")

    menu_items = {"1": "Sandbox Consumer Key",
                  "2": "Live Consumer Key",
                  "3": "Exit"}
    while True:
        print("")
        options = menu_items.keys()
        for entry in options:
            print(entry + ")\t" + menu_items[entry])
        selection = input("Please select Consumer Key Type: ")
        if selection == "1":
            base_url = SANDBOX_BASE_URL
            break
        elif selection == "2":
            base_url = PROD_BASE_URL
            break
        elif selection == "3":
            break
        else:
            print("Unknown Option Selected!")
    print("")

    # Step 1: Get OAuth 1 request token and secret
    request_token, request_token_secret = etrade.get_request_token(
        params={"oauth_callback": "oob", "format": "json"})

    # Step 2: Go through the authentication flow. Login to E*TRADE.
    # After you login, the page will provide a text code to enter.
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter text code from browser: ")

    # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
    session = etrade.get_auth_session(request_token,
                                  request_token_secret,
                                  params={"oauth_verifier": text_code})

    main_menu(session, base_url, text_code)


def main_menu(session, base_url):
    """
    Provides the different options for the sample application: Market Quotes, Account List

    :param session: authenticated session
    """

    menu_items = {"1": "Market Quotes",
                  "2": "Account List",
                  "3": "Exit"}

    while True:
        print("")
        options = menu_items.keys()
        for entry in options:
            print(entry + ")\t" + menu_items[entry])
        selection = input("Please select an option: ")
        if selection == "1":
            market = Market(session, base_url)
            market.quotes()
        elif selection == "2":
            accounts = Accounts(session, base_url)
            accounts.account_list()
        elif selection == "3":
            break
        else:
            print("Unknown Option Selected!")
