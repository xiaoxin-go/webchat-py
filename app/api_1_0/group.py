import random
from flask import current_app
from app import db
from app.models import Group, GroupsToUser, Chat
from app.constants import DEFAULT_IMAGES
from utils.restful import server_error, params_error, success, unauth_error
from .common import BaseHandler


class GroupHandler(BaseHandler):
    """ 群组操作 """

    def get_(self):
        """  获取群组信息 """
        # 若群组ID存在，则只取出该群组信息
        group_id = self.request_data.get('group_id')
        print('..........group_id', group_id)
        if group_id:
            group_obj = self.check_group(group_id)
            if not group_obj:
                return
            self.result = success(data=group_obj.to_json())
            return

        # 如果用户为站长，则返回所有群组信息
        if self.user_obj.type == 0:
            group_query = self.filter_all(Group, '群组信息获取异常')

        # 否则先从群组成员表，获取包含自己的群组ID，通过群组ID获取所在的群组
        else:
            group_user = self.query_(GroupsToUser, {'user_id': self.user_id}, '群组成员获取异常')
            group_ids = [group.group_id for group in group_user]
            try:
                group_query = Group.query.filter(Group.id.in_(group_ids))
            except Exception as e:
                current_app.logger(e)
                self.result = server_error(message='群组信息查询异常')
                return

        # 分页
        #group_obj = group_query.paginate(page=page, per_page=page_size, error_out=False)
        # 对象转换成列表
        group_list = [group.to_json() for group in group_query]
        self.result = success(data=group_list)

    def add_(self):
        """  添加群组信息 """
        print(self.request_data)
        name = self.request_data.get('group_name')
        if not all([self.user_id, name]):
            self.result = params_error()
            return

        # 获取用户，判断用户类型是否正确
        if not self.user_obj or self.user_obj.type not in [0, 1]:
            self.result = unauth_error(message='用户无权限')
            return

        # 设置群组头像，随机从默认图片中选取一张做为头像
        group_logo = self.request_data.get('group_logo')
        if not group_logo:
            group_logo = random.choice(DEFAULT_IMAGES)

        # 添加群组
        group_info = self.request_data.get('info')  # 获取群公告信息
        group_obj = Group(name=name, logo=group_logo, group_info=group_info)
        db.session.add(group_obj)
        if not self.commit('群组已存在', '群组添加异常'):
            return

        print('group_obj...', group_obj.id)

        # 添加群组成员
        group_to_user = GroupsToUser(group_id=group_obj.id, user_id=self.user_id, type=0)
        db.session.add(group_to_user)
        if not self.commit(content2='群组添加异常'):
            return

        self.result = success(message='群组添加成功')

    def put_(self):
        """  修改群组信息，群组名称，头像 """
        group_id = self.request_data.get('group_id')
        group_logo = self.request_data.get('group_logo')
        name = self.request_data.get('name')
        group_info = self.request_data.get('group_info')

        # 用户ID和群组ID必须存在，并且群组名和群组头像至少存在一项
        if not all([group_id, self.user_id]) or (
                all([group_id, self.user_id]) and (not group_logo and not name and not group_info)):
            self.result = params_error()
            return

        # 获取群组信息，判断群组是否存在
        group_obj = self.check_group(group_id)
        if not group_obj:
            return

        # 获取用户信息，判断用户是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        # 判断用户是否有修改群组权限
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 用户不在群组中并且用户非站长， 或者用户在群组中非管理员
        if user_obj.type != 0 and (not group_user_obj or group_user_obj.type not in [0, 1]):
            self.result = unauth_error(message='用户无修改群组权限')
            return

        # 修改群组信息
        if name:
            group_obj.name = name
        if group_logo:
            group_obj.logo = group_logo
        if group_info:
            group_obj.info = group_info

        # 提交修改
        if not self.commit('群组名已存在', '群组修改异常'):
            return

        self.result = success(message='群组修改成功')

    def delete_(self):
        """  删除群组 """
        group_id = self.request_data.get('group_id')

        # 判断参数是否完整
        if not group_id:
            self.result = params_error()
            return

        # 获取群组信息
        group_obj = self.check_group(group_id)
        if not group_obj:
            return

        # 获取用户信息
        user_obj = self.check_user()
        if not user_obj:
            return

        # 获取群组成员信息
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 判断用户不是站长，并且不是群主，则退出该群
        if user_obj.type != 0 and (not group_user_obj or group_user_obj.type != 0):
            group_user = self.check_group_user(self.user_id, group_id)
            if not group_user:
                return
            db.session.delete(group_user)
        else:
            # 删除群组信息
            db.session.delete(group_obj)
            group_user_query = self.query_(GroupsToUser, {'group_id': group_id}, '群组成员信息查询异常')
            if not group_user_query:
                return
            group_user_query.delete()

        if not self.commit(content2='群组信息修改异常'):
            return

        self.result = success(message='群组修改成功')


class QuitGroupHandler(BaseHandler):
    """退出群组"""
    def delete_(self):
        group_id = self.request_data.get('group_id')
        group_user_obj = self.check_group_user(self.user_id, group_id)
        if not group_user_obj:
            return
        # 删除群组成员
        db.session.delete(group_user_obj)

        # 获取聊天
        chat_obj = self.query_(Chat, {'type': 2, 'chat_obj_id': group_id, 'user_id': self.user_id}, '获取聊天信息异常')
        if not chat_obj:
            return

        chat_obj.delete()
        if not self.commit():
            return

        self.result = success(message='退出成功')

