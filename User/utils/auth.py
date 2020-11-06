'''
用户登录接口
'''
# import json
# import os
# import time
import hashlib
import time
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.core.exceptions import ObjectDoesNotExist
from User import models
class TokenAuth(BaseAuthentication):
    '''
    Token
    '''
    def authenticate(self,request):
        #判断是否在headers携带token
        token = request.META.get("HTTP_TOKEN")
        # token = request._request.GET.get('token')
        token_obj = models.User_Token.objects.filter(token = token).first()
        if not token_obj:
            raise exceptions.AuthenticationFailed('用户认证失败')
        #在rest 内部会把他们给request
        return (token_obj.user,token_obj)
    def authenticate_header(self,request):
        pass



def get_token(request):
    '''
    获取token
    '''
    return request.META.get("HTTP_TOKEN")

def get_user(request):
    '''
    获取用户
    '''
    try:
        token = get_token(request)
        obj = models.User_Token.objects.filter(
                    token=token).first()
        return obj.user
    except ObjectDoesNotExist:
        return -1
    return 1


def md5(user):
    '''
    获取md5
    '''
    ctime = str(time.time())
    get_md5 = hashlib.md5(bytes(user, encoding='utf-8'))
    get_md5.update(bytes(ctime, encoding='utf-8'))
    return get_md5.hexdigest()

def update_token(user_account_obj, token):
    '''
    更新token
    '''
    token_obj = models.Token.objects.filter(user_id=user_account_obj).first()
    if not token_obj:
        models.Token.objects.create(user_id=user_account_obj, token=token)
    else:
        models.Token.objects.filter(
            user_id = user_account_obj).update(token=token)
