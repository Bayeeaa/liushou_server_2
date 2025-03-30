import json
import uuid
from functools import wraps

import requests
from Crypto.PublicKey import RSA
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from .utils import generate_jwt, decode_jwt
from django.http import JsonResponse
from alipay import AliPay
import json
from django.views.decorators.csrf import csrf_exempt


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

#应用私钥
app_private_key_string = '-----BEGIN RSA PRIVATE KEY-----\n'+'q9nFYEa65QDRQ4U2kL7tzO9lB1R9Fyacs2cVlv0EM5qcCcRvYRAhoZEUcvFs/YdBey8ft7Tix0SIfEbA11UMiZ2DJbCLVJU8ZsEhyBaiqZnID4k28MDt77MEn1ZwWfO1mBenp+w50vYQgKyg6ka1HHvzvmJcidORCToEEyRfWYYbRwmHSo9eL6eOvTpmd/1FY+Cn/oHumq1QNvnc/jo6dKIrBURg1lVRxncyTzK5/sIs6bnaiTFRKvWGAo6IBgKOKVjHn1dUbq7AVJpZBJGHOT6ZlEsXIrdJnFmD7+7te7k+uBMQdK7tPDg5iSPnjph/VFAgMBAAECggEARkLFjmxl143anN6Af9fVRX+TAzZhs7zlSTqv+nt6/m8iFo1YoTobYUPBZZyX9EO4TSZn5XGst20uXKITVD3Jw8xDlwnRXs6zw1gMkNnrfFHNF4QM39Dilk1s4jJGg9nMEggVoz5JFvtQQHvId5cLME5XclcU/ab8SlvaWARDFV6p8iHTEdFLi40wMP0zcw3jM9WDqZaC4n6TOExhcvlZ17+EeahEWrlQz9Sz1x5HesW7n+xy8RAl/+LT6dLYlNYEjG4jmDdEPbYGk9QiiDC4gz3nUF2H3VVsHm8fxsC1+N7kne5DYNv/OUIL/k4j3HkSijWCxyYXSTLQNkKYIzjbwQKBgQDJJS4aO7cppF0fMMkgYH//dlLw4X6xZpDC7lptPPvTmf+8MOudOYIMCM1DGsC8Jpwk/ITUfaW4KaJNmIHR4LP+J+HIN3RxbhMD6JxltoD3H1TspR0vVsdzgpyptQVm+bLjXsVknc/i/ryP4vsOLVHanHmkMn2F4NQBq/URlFtOtQKBgQDF4zEwk0cpQTiJhPariI5C+ITqipUf6t91Gsp9FsvZGZM2XPBtK4HW8yQo/zBL/RvNK/8xt5rcY0pJSeMI+bLDdurtS5oo+FzlbaXJCm0kLVnSXKem5t2zJ3xD6WFnO4aLdwaa/5bC63ba6BpScOcX9kW9svFW4bVO8+LGhC6WUQKBgQCRQihpCXbcu7YEMFcO6qGE+w4qpq23rzobi8YB3Wh/B1eHsEx23nDr/+875rYJKljY3QOP8K0csfRj1R7rUjqp8GM9E88jmzpgODu5uHKqBBZwT00kQqcG4+v/IpskIm7thCNI5i6a3xuNTX3AXzodhaLS0SOU6ygvjN8OMvU9gQKBgQCfrpk+7Vl6/No2fkjeWi8R86Ct8m4rd0giIyBKmF6eLXkRYSXRsk3vufvv6Rx79R6+DUa8Q8B/HtAPG8RMtdF+0TL5kQwxC1lK+ZPSCsvPaZkVmxbeI2W6753i3yxuNSZ42+9EnAJ3/7HFK44yAFE6kMvuK7t7tF6t+zd/oaJGQQKBgBRnbrh+KrrzyRq46BIZp44AmDf7hH1ZAM0WFqOMBcEzC4BqQLK5jI3wMXEgE5SGlutGbUPggZt/xeW2n23qcyPQqnQ7zSRNsJBrQYM+8ZwRwpdmc+Wp/grmUuBQO9Qmp8Je/WBQyJDOgvUtmJ4C6+lAWLKRgo/11oOk4Z87CWOO'+'\n-----END RSA PRIVATE KEY-----'
#支付宝公钥
alipay_public_key_string = '-----BEGIN RSA PRIVATE KEY-----\n'+'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhrQtIYwReXWqu6Xy5cZkvJIAEuC/7g13oeaxZkgv5eMy+i57fMdR4zASqEsZu+5qr416/RihJU+5HY6hhbpuhbq5vKNM0XVc4rtunh04770QB6SJE+/xR+rEkLo7l9gVdAyf8mh2rtUdGiKkDaTBVcT2iEiVA8xSpJKyK3sHXCE57q+afefwKtXrDq5gaFtJtLA3GLWxtpbE0yxhe8UVxDIN7uMYWeP6QAHEpsRggF8bsE5R8ZWZZgUfUxkAUvfNmIimjgngexzastBlgpX44FXTzKPBhOr/5+7m4moglenhHONxHYpJcNDKUUu7i8S8uvPMFjXh+UtCmYFA2C/06wIDAQAB'+'\n-----END RSA PRIVATE KEY-----'

@csrf_exempt
def create_alipay_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = data.get("amount")

        # 生成唯一订单号
        order_id = str(uuid.uuid4()).replace("-", "")

        alipay = AliPay(
            appid="2021005133632285",
            app_notify_url=None,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=False,  # 沙箱模式
        )

        # 生成支付订单
        order_string = alipay.api_alipay_trade_precreate(
            subject="公益捐赠",
            out_trade_no=order_id,
            total_amount=str(amount),
            notify_url="http://47.120.56.172/api/alipay/notify",
        )

        print(order_string)

        # 获取支付宝返回的支付二维码链接
        qr_code_url = order_string.get("qr_code")

        return JsonResponse({
            "qr_code_url": qr_code_url,
            "order_id": order_id
        })


@csrf_exempt
def check_alipay_status(request):
    if request.method == "GET":
        order_id = request.GET.get("order_id")

        if not order_id:
            return JsonResponse({"status": "error", "message": "缺少订单号"}, status=400)

        alipay = AliPay(
            appid="2021005133632285",
            app_notify_url=None,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True,
        )

        result = alipay.api_alipay_trade_query(out_trade_no=order_id)

        if result.get("trade_status") == "TRADE_SUCCESS":
            return JsonResponse({
                "status": "success",
                "amount": result["total_amount"],
                "order_id": order_id
            })
        else:
            return JsonResponse({"status": "pending"})

@csrf_exempt
def alipay_notify(request):
    if request.method == "POST":
        # 获取支付宝回调的参数
        data = request.POST

        # 你自己的商户私钥和支付宝公钥
        alipay = AliPay(
            appid="2021005133632285",
            app_notify_url=None,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=False,  # 沙箱模式
        )

        # 验证签名，防止伪造通知
        success = alipay.verify(data)

        if success:
            # 获取支付宝返回的支付信息
            order_id = data.get('out_trade_no')
            trade_status = data.get('trade_status')

            if trade_status == "TRADE_SUCCESS":
                # 支付成功，可以更新订单状态
                return JsonResponse({"status": "success"})
            else:
                # 交易没有成功
                return JsonResponse({"status": "failure", "message": "支付未成功"})

        else:
            # 如果签名不匹配，拒绝处理
            return JsonResponse({"status": "failure", "message": "签名验证失败"})

    return JsonResponse({"status": "failure", "message": "无效请求"})