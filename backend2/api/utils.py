import jwt
import datetime
from django.conf import settings

def generate_jwt(user):
    """ 生成 JWT Token """
    payload = {
        "id": user.id,
        "nickname": user.nickname,
        "exp": datetime.datetime.utcnow() + settings.JWT_EXPIRATION_DELTA,  # 过期时间
        "iat": datetime.datetime.utcnow(),  # 签发时间
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt(token):
    """ 解析 JWT Token """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload  # 返回解码后的用户信息
    except jwt.ExpiredSignatureError:
        return None  # Token 过期
    except jwt.InvalidTokenError:
        return None  # 无效 Token
