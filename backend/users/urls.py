from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('', UserApiView.as_view(), name='users'),
    path('<uuid:pk>', UserSingleApiView.as_view(), name='user'),
    path('login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', UserRegistrationAPIView.as_view(), name='register_user'),
    path('logout', UserLogoutAPIView.as_view(), name='logout_user'),
]
