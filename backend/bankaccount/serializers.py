from rest_framework import serializers

from bankaccount.utils import PlaidUtils
from bankaccount.models import PlaidLinkAccount, PlaidAccountTransaction
from bankaccount.tasks import get_item_and_account_details


class PlaidLinkAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaidLinkAccount
        fields = ['account_id', 'name', 'mask', 'type', 'sub_type', 'balance', 'currency']


class PlaidAccountTransactionSerializer(serializers.ModelSerializer):
    plaid_link_account = PlaidLinkAccountSerializer()

    class Meta:
        model = PlaidAccountTransaction
        fields = ['plaid_link_account', 'transaction_id', 'name', 'merchant_name', 'transaction_type', 'amount']


class AccessTokenSerializer(serializers.Serializer):
    public_token = serializers.CharField()

    def create(self, validated_data):
        try:
            access_token, item_id = PlaidUtils.exchange_public_token(validated_data['public_token'])
            if(access_token and item_id):
                data = {
                    'access_token' : access_token,
                    'item_id' : item_id,
                    'user_id' : self.context['request'].user.uuid
                }
                get_item_and_account_details.delay(data)
            return validated_data
        except Exception as e:
            print(e)
            raise serializers.ValidationError({'public_token': 'Please provide valid token.'})
