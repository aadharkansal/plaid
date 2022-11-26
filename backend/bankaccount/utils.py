import base64
import traceback
from datetime import datetime, timedelta

from django.db.models import CharField
from django.utils.translation import gettext as _
from decouple import config
from cryptography.fernet import Fernet
import plaid
from decouple import config

from bankaccount.models import *


class EncryptedField(CharField):
    """
    Custom model field to store sensitive data
    """
    def __init__(self, *args, db_collation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_size = 16
        self.cipher = Fernet(base64.urlsafe_b64encode(str.encode(config('SECRET_KEY')[:32])))
    def pad(self, value):
        return value + (self.block_size - len(value) % self.block_size) * chr(
            self.block_size - len(value) % self.block_size
        )
    def unpad(self, value):
        return value[: -ord(value[len(value) - 1:])]
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.unpad(self.cipher.decrypt(bytes(str.encode(value)))).decode()
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(bytes(str.encode(self.pad(value)))).decode()
    


class PlaidUtils():

    @staticmethod
    def get_plaid_client():
        return plaid.Client(client_id = config('PLAID_CLIENT_ID'),
                        secret = config('PLAID_SECRET_KEY'),
                        environment = config('PLAID_ENVIRONMENT'))

    @staticmethod
    def create_link_token(user_id):
        try:
            configs = {
                    'user': {
                        'client_user_id': str(user_id),
                    },
                    'client_name': 'Testing',
                    'country_codes': ['US'],
                    'language': 'en',
                    'webhook': config('PLAID_WEBHOOK_URL'),
                }
            configs['products'] = ["transactions"]
            configs['account_filters'] = {
                    'depository': {
                        'account_subtypes': ['checking','savings','money market','paypal','prepaid'],
                    },
                    'credit': {
                        'account_subtypes': ['credit card','paypal'],
                    },
                }
            configs['redirect_uri'] = config('redirect_uri')
            client = PlaidUtils.get_plaid_client()
            response = client.LinkToken.create(configs)
            return response['link_token']
        except plaid.errors.BaseError as e:
            print(e)
            return None

    @staticmethod
    def exchange_public_token(public_token):
        try:
            client = PlaidUtils.get_plaid_client()
            response = client.Item.public_token.exchange(public_token)
            return response['access_token'], response['item_id']
        except plaid.errors.BaseError as e:
            print(e)
            return None
    
    @staticmethod
    def get_item_details(access_token):
        try:
            client = PlaidUtils.get_plaid_client()
            item = client.Item.get(access_token)
            return item['item']
        except plaid.errors.BaseError as e:
            print(e)
            return None

    @staticmethod
    def get_institution_details(institution_id, country_codes):
        client = PlaidUtils.get_plaid_client()
        try:
            institution = client.Institutions.get_by_id(institution_id, country_codes,
                                                        {'include_optional_metadata': True})
            return institution['institution']
        except plaid.errors.BaseError as e:
            print(e)
            return None

    @staticmethod
    def get_plaid_account_details(access_token):
        client = PlaidUtils.get_plaid_client()
        try:
            try:
                accounts = client.Accounts.balance.get(access_token,_options = {'min_last_updated_datetime' : (datetime.now()-timedelta(days=config('PLAID_ACCOUNT_FETCH_DAYS'))).strftime("%Y-%m-%dT%H:%M:%SZ")})
            except plaid.errors.BaseError as e:
                if e.code == 'ITEM_LOGIN_REQUIRED':
                    print("required login try refreshing tokens...")
                return None
            accounts = accounts.get('accounts')
            depository_accounts = [account for account in accounts if account.get('type') == 'depository']
            auth_accounts = []
            if len(depository_accounts) > 0:
                try:
                    auth_accounts = client.Auth.get(access_token)
                    auth_accounts = [acc.get('account_id') for acc in auth_accounts.get('numbers').get('ach')]
                except plaid.errors.BaseError as e:
                    if e.code == 'NO_AUTH_ACCOUNTS':
                        auth_accounts = []
            plaid_link_accounts = []
            for account in accounts:
                plaid_link_account = PlaidLinkAccount.objects.create(
                    balance = round(float(account.get('balances').get('current')), 4),
                    currency = account.get('balances').get('iso_currency_code'),
                    account_id =  account.get('account_id'),
                    name = account.get('name'),
                    mask = account.get('mask'),
                    subtype = account.get('subtype'),
                    type = account.get('type'),
                )
                plaid_link_accounts.append(plaid_link_account)
            return plaid_link_accounts
        except BaseErplaid.errors.BaseErrorror as e:
            print(e)
            return None
    
    @staticmethod
    def fetch_and_save_account_transactions(access_code, account_id=None, transaction_count=0):
        try:
            client = PlaidUtils.get_plaid_client()
            end_date = datetime.today().strftime("%Y-%m-%d")
            start_date = (datetime.today() - timedelta(days=config('ACCOUNT_FETCH_DAYS'))).strftime("%Y-%m-%d")
            if account_id:
                response = client.Transactions.get(
                    access_code,
                    account_ids=[account_id],
                    start_date=start_date,
                    end_date=end_date,
                )
                transactions = response["transactions"]
                while len(transactions) < response["total_transactions"]:
                    response = client.Transactions.get(
                        access_code,
                        account_ids=[account_id],
                        start_date=start_date,
                        end_date=end_date,
                        offset=len(transactions),
                    )
                    transactions.extend(response["transactions"])
            elif transaction_count:
                response = client.Transactions.get(
                    access_code,
                    count=transaction_count,
                    start_date=start_date,
                    end_date=end_date,
                )
                transactions = response["transactions"]
            else:
                return
            for transaction in transactions:
                try:
                    plaid_link_account = PlaidLinkAccount.objects.filter(account_id=transaction["account_id"]).first()
                    if plaid_link_account:
                        plaid_account_transaction = PlaidAccountTransaction.objects.create(
                            plaid_link_account = plaid_link_account,
                            transaction_id = transaction["transaction_id"],
                            name = transaction["name"],
                            merchant_name = transaction["merchant_name"],
                            transaction_type = transaction["transaction_type"],
                            amount = transaction["amount"]
                        )
                except Exception as e:
                    print(e)
                    return
        except Exception as e:
            print(e)
            return
