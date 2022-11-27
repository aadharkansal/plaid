from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import AccessTokenAPIView, UserTransactionAccountAPIView

urlpatterns = [
    path('plaid_access_token', AccessTokenAPIView.as_view(), name='plaid_access_token'),
    path('user_transaction_account', UserTransactionAccountAPIView.as_view(), name='user_transaction_account')
]
