from flask import current_app, request
from app import db
from app.models import User
from utils.restful import server_error, params_error, success, unauth_error
from .common import BaseHandler

import random


class UserHandler(BaseHandler):
    """ 用户操作 """

    def get_(self):
        """  查询用户 """
        print('request_data:', self.request_data)
        username = self.request_data.get('username')

        # 判断用户是否拥有查询用户权限， 只有站长和副站长拥有查询权限
        if self.user_obj.type not in [0, 1]:
            self.result = unauth_error(message='无操作权限')
            return

        user = self.query_(User, {'username': username}, '用户信息获取异常').first()
        print('username:', username)
        data = user.to_dict() if user else {}
        print(data)
        self.result = success(data=data)

    def add_(self):
        """  注册用户 """

        # username = self.request_data.get('username')
        # password = self.request_data.get('password')
        # nickname = self.request_data.get('nickname')
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        # 检查用户名和密码是否存在
        if not all([username, password, nickname]):
            self.result = params_error(message='缺少必要参数')
            return

        logos = ['mingren.jpeg', 'mingren1.jpg', 'xiaoli1.jpeg', 'xiaoying1.jpeg', 'you1.jpg', 'zilanye1.jpg', 'zouzu1.jpg']
        logo = '/static/logo/%s' % random.choice(logos)
        # 添加用户
        user_obj = User(username=username, nickname=nickname, logo=logo)

        # 设置密码
        user_obj.password = password  # 已自动加密
        db.session.add(user_obj)

        if not self.commit('用户已存在', '用户添加异常'):
            return

        # 注册成功
        self.result = success(message='注册成功')

    def put_(self):
        """  用户修改 """

        logo = self.request_data.get('logo')
        nickname = self.request_data.get('nickname')
        password = self.request_data.get('password')
        type = self.request_data.get('type')
        if not any([logo, nickname, password, type]):
            self.result = params_error()
            return
        if not self.user_obj:
            return

        # 修改用户密码
        if password:
            self.user_obj.password = password
        elif nickname:
            self.user_obj.nickname = nickname
        elif logo:
            self.user_obj.logo = logo
        else:
            self.user_obj.type = type

        if not self.commit(content2='修改用户信息异常'):
            return

        self.result = success(message='修改成功')

    def delete_(self):
        """  用户删除 """


class UserInfoHandler(BaseHandler):
    def get_(self):
        user_id = self.request_data.get('user_id')
        user_obj = self.check_user(user_id)
        if not user_obj:
            return
        self.result = success(data=user_obj.to_dict())
