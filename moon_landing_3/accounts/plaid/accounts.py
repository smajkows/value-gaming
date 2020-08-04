from moon_landing_3.accounts.accounts import AbstractAccountHandler, NdbDailyAccountStats, NdbAccount, NdbTransaction, \
    NdbAccessItem
import datetime
from google.cloud import ndb
from moon_landing_3.utilities import plaid_client

ndb_client = ndb.Client()


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
                          subtype=account['subtype'],
                          platform_id=account['institution_id'],
                          plaid_item_entity=ndb.Key(PlaidItem, account['item_id']))
        acct.put()
        return

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
            self.create_account_from_api(account)
        return

    def poll_daily_account_stats(self, account):
        profile = account.plaid_item_entity.get()
        access_token = profile.access_token
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        balance_info = plaid_client.Holdings.get(access_token)
        self.create_daily_stats_from_api(balance_info)
        transaction_info = plaid_client.InvestmentTransactions.get(access_token, '2000-01-01', today_str,
                                                _options=None, account_ids=[account.account_id])
        print('-------------------')
        print(transaction_info)
        print('-------------------')
        #self.create_transactions_from_api(transaction_info)
        return

    def create_transactions_from_api(self, transaction_info):
        return
        # set this should be the same for all transactions
        account_id = '{}_{}'.format(self.PLATFORM, transaction_info['account_id'])
        for transaction in transaction_info['transactions']:
            transaction_id = transaction.get('orderId')
            if not transaction_id:
                print('skipping item no transactionId')
                continue

            id = '{}_{}'.format(self.PLATFORM, transaction_id)

            transaction_item = transaction['transactionItem']
            if not transaction_item:
                continue

            type = transaction['type']
            s_date_str = transaction['settlementDate'].split('T')[0]
            settlement_date = datetime.datetime.strptime(s_date_str, '%Y-%m-%d')
            print('settlement date: {}'.format(settlement_date))

            t_date_str = transaction['transactionDate'].split('T')[0]
            transaction_date = datetime.datetime.strptime(t_date_str, '%Y-%m-%d')

            transaction_id = str(transaction['transactionId'])
            description = transaction['description']

            amount = transaction_item.get('amount', None)
            price = transaction_item.get('price', None)
            cost = transaction_item['cost']
            instruction = transaction_item.get('instruction', None)
            instrument = transaction_item.get('instrument')

            symbol = instrument['symbol'] if instrument else None
            asset_type = instrument['assetType'] if instrument else None

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
                    positions.append({
                        'instrument': {
                            'symbol': security_dict[holding['security_id']]
                        },
                        'averagePrice': holding['cost_basis'] / holding['quantity'],
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
