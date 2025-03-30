from django.urls import path
from .views import (
    RegisterView,
    login_view,
    chat,
    create_alipay_order,
    check_alipay_status
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path("login/", login_view, name="login"),
    path('chat/', chat, name="chat"),

    # 支付宝支付相关接口
    path("alipay/create/", create_alipay_order, name="create-alipay-order"),
    path("alipay/status/", check_alipay_status, name="check-alipay-status"),
]
