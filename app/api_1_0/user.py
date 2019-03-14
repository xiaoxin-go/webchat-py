from flask import current_app
from app import db
from app.models import User
from utils.restful import server_error, params_error, success, unauth_error
from .common import BaseHandler


class UserHandler(BaseHandler):
    """ 用户操作 """

    def get_(self):
        """  查询用户 """
        username = self.request_data.get('username')

        if not self.user_id:
            self.result = params_error()
            return

        # 判断用户是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        # 判断用户是否拥有查询用户权限， 只有站长和副站长拥有查询权限
        if user_obj.type not in [0, 1]:
            self.result = unauth_error(message='无操作权限')
            return

        try:
            user_query = User.query.filter(User.username == username) if username else User.query.filter()
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='用户查询异常')
            return

        total = user_query.count()
        data_list = [user.to_dict for user in user_query]
        self.result = success(data=data_list)

    def add_(self):
        """  注册用户 """

        username = self.request_data.get('username')
        password = self.request_data.get('password')
        nickname = self.request_data.get('nickname')

        # 检查用户名和密码是否存在
        if not all([username, password, nickname]):
            self.result = params_error(message='缺少必要参数')
            return

        # 添加用户
        user_obj = User(username=username, nickname=nickname)

        # 设置密码
        user_obj.password = password  # 已自动加密
        db.session.add(user_obj)

        if not self.commit('用户已存在', '用户添加异常'):
            return

        # 注册成功
        self.result = success(message='注册成功')

    def put_(self):
        """  用户修改 """

        username = self.request_data.get('username')
        if not username:
            self.result = params_error(message='缺少必要参数')
            return
        old_password = self.request_data.get('old_password')

        try:
            user_obj = User.query.filter_by(username=username).first()
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='获取用户信息失败')
            return

        if not user_obj:
            self.result = unauth_error(message='用户信息不存在')
            return

        # 如果密码存在，则为修改密码
        if old_password:
            new_password = self.request_data.get('new_password')
            if not new_password:
                self.result = params_error(message='缺少必要参数')
                return

            # 原密码不正确
            if not user_obj.check_password(old_password):
                self.result = params_error(message='原密码不正确')
                return

            # 检验成功，修改用户密码
            user_obj.password = new_password
            if not self.commit(content2='修改密码异常'):
                return

            self.result = success(message='密码修改成功')
        # 否则为修改昵称
        else:
            nickname = self.request_data.get('nickname')
            if not nickname:
                self.result = params_error(message='缺少必要参数')
                return

            user_obj.nickname = nickname
            if not self.commit(content2='修改昵称异常'):
                return

            self.result = success(message='用户昵称修改成功')

    def delete_(self):
        """  用户删除 """

    def user_info(self):
        user_obj = self.check_user()
        if not user_obj:
            return

        self.result = success(data=user_obj.to_dict)
