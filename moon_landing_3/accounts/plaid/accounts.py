from moon_landing_3.accounts.accounts import AbstractAccountHandler, NdbDailyAccountStats, NdbAccount, NdbTransaction, \
    NdbAccessItem
import datetime
from google.cloud import datastore, ndb
from moon_landing_3.utilities import plaid_client

ndb_client = ndb.Client()
client = datastore.Client()


class PlaidItem(NdbAccessItem):
    pass


class PlaidAccount(NdbAccount):
    account_name = ndb.StringProperty()  #
    account_screen_name = ndb.StringProperty()  # optional display name for the account
    mask = ndb.StringProperty()
    type = ndb.StringProperty()
    subtype = ndb.StringProperty()
    platform_id = ndb.StringProperty()  # the id of the platform from plaid
    plaid_item_entity = ndb.KeyProperty(required=True)  # the key for the plaid item which holds the access token


class PlaidAccountHandler(AbstractAccountHandler):
    PLATFORM = 'plaid'
    MODEL = PlaidAccount
    TRANSACTION_MODEL = NdbTransaction
    DAILY_STATS_MODEL = NdbDailyAccountStats

    def create_account_from_api(self, account):
        acct = self.MODEL(id='{}_{}'.format(self.PLATFORM, account['id']),
                          account_id=account['id'],
                          account_name=account['name'],
                          user_id=account['user_id'],  # user id from firebase auth
                          platform=self.PLATFORM,
                          platform_name=account['platform'],
                          type=account['type'],
                          mask=account['mask'],
                          account_screen_name=None,
                          subtype=account['subtype'],
                          platform_id=account['institution_id'],
                          plaid_item_entity=ndb.Key(PlaidItem, account['item_id']))
        acct.put()
        return acct

    def create_accounts_from_api(self, api_response, item_id, user_id, access_token):
        for account in api_response['metadata']['accounts']:
            account['user_id'] = user_id  # pass the user_id from firebase as part of the account json
            account['item_id'] = item_id  # pass the plaid item_id for the account
            account['platform'] = api_response['metadata']['institution']['name']
            account['institution_id'] = api_response['metadata']['institution']['institution_id']
            item = ndb.Key(PlaidItem, account['item_id']).get()
            if not item:
                item = PlaidItem(id=item_id, access_token=access_token)
                item.put()
            account_entity = self.create_account_from_api(account)
            self.poll_daily_account_stats(account_entity)
        return

    def poll_daily_account_stats(self, account):
        profile = account.plaid_item_entity.get()
        access_token = profile.access_token
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        balance_info = plaid_client.Holdings.get(access_token)
        update_webhook = plaid_client.Item.webhook.update(access_token, 'http://project-moon-landing.appspot.com/item/plaid/webhook')
        self.create_daily_stats_from_api(balance_info)
        query = client.query(kind='NdbTransaction', order=('-transaction_date',))
        latest_transactions = query.fetch(1)
        if not latest_transactions:
            # if there is no latest transaction on this account set latest date to 2000
            latest_date = '2000-01-01'
            print('latest date was none and set to 2000')
        else:
            latest_date = '2020-01-01'
            for item in latest_transactions:
                latest_date = item['transaction_date'].strftime("%Y-%m-%d")
                break
            print('latest date not none {}'.format(latest_date))
        transaction_info = plaid_client.InvestmentTransactions.get(access_token, latest_date, today_str,
                                                                   _options=None, account_ids=[account.account_id])
        securities = {}
        for security in transaction_info['securities']:
            securities.update({
                security['security_id']: security
            })
        self.create_transactions_from_api(transaction_info, securities)
        return

    def create_transactions_from_api(self, transaction_info, securities):
        # set this should be the same for all transactions
        for transaction in transaction_info['investment_transactions']:
            account_id = '{}_{}'.format(self.PLATFORM, transaction['account_id'])
            transaction_id = transaction.get('investment_transaction_id')
            id = '{}_{}'.format(self.PLATFORM, transaction_id)

            type = transaction['type']
            s_date_str = transaction['date']
            settlement_date = datetime.datetime.strptime(s_date_str, '%Y-%m-%d')

            t_date_str = transaction['date']
            transaction_date = datetime.datetime.strptime(t_date_str, '%Y-%m-%d')
            description = transaction['name']

            amount = transaction['quantity']
            price = transaction['price']
            cost = transaction['amount']
            instruction = transaction.get('subtype', None)
            security_id = transaction['security_id']

            symbol = securities[security_id]['ticker_symbol']
            asset_type = securities[security_id]['type']

            if ndb.Key(self.MODEL, account_id).get():
                # Only create daily stats for an account if we can find the account it belongs to
                account_key = ndb.Key(self.MODEL, account_id)
                transaction_ndb_item = self.TRANSACTION_MODEL(id=id,
                                                              account=account_key,
                                                              type=type,
                                                              settlement_date=settlement_date,
                                                              transaction_date=transaction_date,
                                                              transaction_id=transaction_id,
                                                              description=description,
                                                              amount=amount,
                                                              price=price,
                                                              cost=cost,
                                                              instruction=instruction,
                                                              symbol=symbol,
                                                              asset_type=asset_type)
                print('putting transaction in db {}'.format(transaction_ndb_item))
                transaction_ndb_item.put()
        return

    def create_daily_stats_from_api(self, balance_info):
        """
        """
        security_dict = {}
        for security in balance_info['securities']:
            security_dict.update({
                security['security_id']: security['ticker_symbol']
            })

        for account in balance_info['accounts']:
            positions = []
            account_id = account['account_id']
            current_balance = account['balances']['current']
            cash_balance = account['balances']['available'] or 0

            for holding in balance_info['holdings']:
                if holding['account_id'] == account['account_id']:
                    print("holding for account id {}: {}".format(account['account_id'], holding))
                    # TODO: remove this hack
                    try:
                        average_price = holding.get('cost_basis', 0) / holding['quantity']
                    except:
                        average_price = 0

                    positions.append({
                        'instrument': {
                            'symbol': security_dict[holding['security_id']]
                        },
                        'averagePrice': average_price,
                        'longQuantity': holding['quantity'],
                        'marketValue': holding['institution_value'],
                        'currentDayProfitLossPercentage': None
                    })

            id = '{}_{}_{}'.format(self.PLATFORM, account_id, datetime.date.today())
            account_id = '{}_{}'.format(self.PLATFORM, account_id)

            if ndb.Key(self.MODEL, account_id).get():
                # Only create daily stats for an account if we can find the account it belongs to
                account_key = ndb.Key(self.MODEL, account_id)
                daily_stats = self.DAILY_STATS_MODEL(id=id,
                                                     balance=current_balance,
                                                     date=datetime.datetime.today(),
                                                     cash_balance=cash_balance,
                                                     account=account_key,
                                                     positions=positions)
                daily_stats.put()
                account_entity = account_key.get()
                account_entity.update_account_balance()
        return
