from django.urls import path
from .views import RegisterView, login_view, chat

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path("login/", login_view, name="login"),
    path('chat/',chat, name="chat")
]