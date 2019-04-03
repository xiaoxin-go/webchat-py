from flask import request, current_app, session
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Group, GroupsToUser, Friends, Chat
from utils.restful import server_error,unauth_error
import time

def now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


class BaseHandler:
    def __init__(self):
        self.result = {}
        self.request_data = {}
        self.user_id = session.get('id')
        self.user_obj = self.check_user()
        if not self.user_obj and not (request.path.split('/')[-1] == 'user' and request.method == 'POST'):
            return

        if request.method == 'GET':
            self.request_data = request.values
            self.get_()
        elif request.method == 'POST':
            self.request_data = request.json
            self.add_()
        elif request.method == 'PUT':
            self.request_data = request.json
            self.put_()
        elif request.method == 'DELETE':
            self.request_data = request.values
            self.delete_()

    def get_(self):
        pass

    def add_(self):
        pass

    def put_(self):
        pass

    def delete_(self):
        pass

    def check_user(self, user_id=None):
        """  检查用户是否存在 """
        user_id = user_id or self.user_id
        try:
            user_obj = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='用户查询异常')
            return

        if not user_obj:
            self.result = unauth_error(message='用户不存在')
            return
        return user_obj

    def check_group(self, group_id):
        """  检查群组是否存在 """
        # 获取用户信息
        user_obj = self.check_user()
        if not user_obj:
            return

        # 判断用户是否在群组中
        group_user = self.check_group_user(self.user_id, group_id)
        if not group_user and user_obj.type != 0:
            self.result = unauth_error(message='权限异常')
            return

        try:
            group_obj = Group.query.get(group_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='群组查询异常')
            return

        if not group_obj:
            self.result = unauth_error(message='群组不存在')
            return
        return group_obj

    def check_group_user(self, user_id, group_id):
        """  检查用户是否在群组中 """
        try:
            group_user_obj = GroupsToUser.query.filter_by(user_id=user_id, group_id=group_id).first()
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='群组成员查询异常')
            return

        if not group_user_obj:
            self.result = unauth_error(message='权限异常')
            return

        return group_user_obj

    def check_friend(self, user_id, friend_id):
        """  检查好友信息是否存在 """
        try:
            friend_obj = Friends.query.filter_by(user_id=self.user_id, friend_id=friend_id).first()
            print('check_friend',friend_obj)
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='好友信息获取异常')
            return
        return friend_obj

    def check_chat(self, chat_id):
        """  检查聊天是否存在 """
        try:
            chat_obj = Chat.query.get(chat_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message='聊天信息查询异常')
            return

        if not chat_obj:
            self.result = unauth_error(message='聊天不存在')
        return chat_obj

    def query_(self, obj, sql, content):
        """  异常查询 """
        try:
            query_obj = obj.query.filter_by(**sql)
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message=content)
            return
        return query_obj

    def filter_all(self, obj, content):
        """  获取所有数据 """
        try:
            query_obj = obj.query.filter()
        except Exception as e:
            current_app.logger.error(e)
            self.result = server_error(message=content)
            return
        return query_obj

    def commit(self, content1=None, content2=None):
        try:
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            # 此错误信息表示用户被注册过
            current_app.logger.error(e)
            self.result = server_error(message=content1)
            return
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            self.result = server_error(message=content2)
            return

        print('session...success')
        return True
