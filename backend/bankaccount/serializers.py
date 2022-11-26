from rest_framework import serializers

from bankaccount.utils import PlaidUtils
from bankaccount.models import UserPlaidLink
from bankaccount.tasks import get_item_and_account_details


class AccessTokenSerializer(serializers.Serializer):
    public_token = serializers.CharField()

    def create(self, validated_data):
        access_token, item_id = PlaidUtils.exchange_public_token(validated_data['public_token'])
        raise ValueError()
        try:
            if(access_token and item_id):
                user_plaid_link = UserPlaidLink.objects.create(
                    user = self.user,
                    access_code = access_token,
                    item_id = item_id
                )
                get_item_and_account_details.delay(user_plaid_link, access_token)
            return validated_data['public_token']
        except Exception as e:
            print(e)
            raise ValueError()
