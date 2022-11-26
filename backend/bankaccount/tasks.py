from celery import shared_task
from bankaccount.utils import PlaidUtils
from bankaccount.models import PlaidInstitution, PlaidLinkAccount


@shared_task
def get_item_and_account_details(user_plaid_link, access_token):
    client = PlaidUtils.get_plaid_client()
    item = client.Item.get(access_token)
    institution = PlaidUtils.get_institution_details(item['item']['institution_id'], ['US'])
    if institution:
        institution = PlaidInstitution.objects.create(
            plaid_institution_id = institution['institution_id'],
            name = institution['name'],
            url = institution['url']
        )
        user_plaid_link.institution = institution
    plaid_accounts_details = PlaidUtils.get_plaid_account_details(access_token)
