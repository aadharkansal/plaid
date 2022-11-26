import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from jose import jwt
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bankaccount.models import *
from bankaccount.serializers import AccessTokenSerializer
from bankaccount.utils import PlaidUtils


class AccessTokenView(CreateModelMixin, GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AccessTokenSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@csrf_exempt
@require_POST
def plaid_webhook_endpoint(request):
    try:
        data = json.loads(request.body)
        if 'new_transactions' not in data:
            return HttpResponse(status=200)
        transaction_count = data["new_transactions"]
        webhook_type = data["webhook_type"]
        webhook_code = data["webhook_code"]
        item_id = data["item_id"]
        user_plaid_link = UserPlaidLink.objects.filter(item_id=item_id).first()
        if not user_plaid_link:
            return HttpResponse(status=200)
        user = user_plaid_link.user
        if not user.is_active:
            return HttpResponse(status=200)
        """
        ToDo - verify with plaid
        """
        if webhook_type == "TRANSACTIONS":
            if webhook_code == "DEFAULT_UPDATE":
                if user_plaid_link and transaction_count:
                    PlaidUtils.fetch_and_save_account_transactions(
                        access_code=user_plaid_link.access_code, transaction_count=transaction_count
                    )
    except Exception as e:
        print(e)
    return HttpResponse(status=200)

