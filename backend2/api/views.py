from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

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

        # 使用 `check_password()` 进行哈希密码验证
        if check_password(password, user.password):
            return JsonResponse({"success": True, "message": "登录成功"})
        else:
            return JsonResponse({"success": False, "message": "密码错误"}, status=400)

    return JsonResponse({"success": False, "message": "无效请求"}, status=400)