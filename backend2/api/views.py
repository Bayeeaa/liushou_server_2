import json
from functools import wraps

import requests
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from .utils import generate_jwt, decode_jwt


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # 存储数据到数据库
            serializer.save()
            return Response({"message": "注册成功"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login_view(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        nickname = data.get("nickname")
        password = data.get("password")

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "用户不存在"}, status=400)

        if check_password(password, user.password):
            token = generate_jwt(user)
            return JsonResponse({"success": True, "token": token, "name": user.name,
                                 "identity": user.identity, "message": "登录成功"})
        else:
            return JsonResponse({"success": False, "message": "密码错误"}, status=400)

    return JsonResponse({"success": False, "message": "无效请求"}, status=400)


def jwt_required(view_func):
    """ JWT 认证装饰器 """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"success": False, "message": "未提供 Token"}, status=401)

        token = auth_header.split(" ")[1]
        payload = decode_jwt(token)

        if not payload:
            return JsonResponse({"success": False, "message": "Token 无效或已过期"}, status=401)

        try:
            request.user = User.objects.get(id=payload["id"])
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "用户不存在"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


@jwt_required
def protected_view(request):
    return JsonResponse({"success": True, "message": "你已成功访问受保护的接口！", "user": request.user.nickname})


DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'

def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            response = call_deepseek_api(user_message)
            ai_reply = response.get('choices', [{}])[0].get('message', {}).get('content', '')

            return JsonResponse({'reply': ai_reply})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def call_deepseek_api(user_message):
    url = DEEPSEEK_API_URL
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '
    }
    payload = json.dumps({
        "messages": [
            {
                "content": "情感分析师",
                "role": "system"
            },
            {
                "content": user_message,
                "role": "user"
            }
        ],
        "model": "deepseek-chat",
        "frequency_penalty": 0,
        "max_tokens": 2048,
        "presence_penalty": 0,
        "response_format": {
            "type": "text"
        },
        "stop": None,
        "stream": False,
        "stream_options": None,
        "temperature": 1,
        "top_p": 1,
        "tools": None,
        "tool_choice": "none",
        "logprobs": False,
        "top_logprobs": None
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()
