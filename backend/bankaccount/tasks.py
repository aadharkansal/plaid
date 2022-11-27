from celery import shared_task
from bankaccount.utils import PlaidUtils
from bankaccount.models import PlaidInstitution, UserPlaidLink
from users.models import User


@shared_task
def get_item_and_account_details(data):
    client = PlaidUtils.get_plaid_client()
    item = client.Item.get(data.get('access_token'))
    institution = PlaidUtils.get_institution_details(item['item']['institution_id'], ['US'])
    if len(UserPlaidLink.objects.filter(item_id=data.get('item_id'))) is 0:
        user = User.objects.get(uuid=data.get('user_id'))
        user_plaid_link = UserPlaidLink.objects.create(
            user = user,
            access_code = data.get('access_token'),
            item_id = data.get('item_id')
        )
    else:
        user_plaid_link = UserPlaidLink.objects.get(item_id=data.get('item_id'))
    if institution:
        if len(PlaidInstitution.objects.filter(plaid_institution_id=institution['institution_id'])) is 0:
            institution = PlaidInstitution.objects.create(
                plaid_institution_id = institution['institution_id'],
                name = institution['name'],
                url = institution['url']
            )
        else:
            institution = PlaidInstitution.objects.get(plaid_institution_id=institution['institution_id'])
        user_plaid_link.institution = institution
        user_plaid_link.save()
    plaid_accounts_details = PlaidUtils.get_plaid_account_details(data.get('access_token'), user_plaid_link)
    print(plaid_accounts_details)
