from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('plaid_access_token', AccessTokenView.as_view(), name='plaid_access_token'),
]
