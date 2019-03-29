from flask import current_app
from app import db
from app.models import GroupsToUser
from utils.restful import server_error, params_error, success, unauth_error
from .common import BaseHandler


class GroupUserHandler(BaseHandler):
    """  群成员操作 """

    def get_(self):
        """  获取群成员信息 """
        group_id = self.request_data.get('group_id')
        if not all([group_id, self.user_id]):
            self.result = params_error()
            return

        # 获取成员是否在群组中
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 判断用户是否拥有添加成员权限，判断是否为站长，或者是否为群主或群管理员
        if self.user_obj.type != 0 and not group_user_obj:
            self.result = unauth_error(message='用户无权限')
            return

        # 获取成员列表
        group_user_query = self.query_(GroupsToUser, {'group_id': group_id}, '群组成员获取异常')
        if not group_user_query:
            return

        data_list = []
        for group_user in group_user_query:
            user = self.check_user(group_user.user_id)
            if user:
                user_data = user.to_dict()
                user_data['type'] = group_user.type
                data_list.append(user_data)

        self.result = success(data=data_list)

    def add_(self):
        """  添加群成员 """
        group_id = self.request_data.get('group_id')
        member_list = self.request_data.get('member_list')
        print(member_list)

        # 判断参数是否完整
        if not all([group_id, self.user_id, member_list]):
            self.result = params_error()
            return

        # 获取成员是否在群组中
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 判断用户是否拥有添加成员权限，判断是否为站长，或者是否为群主或群管理员
        if self.user_obj.type != 0 and (not group_user_obj or group_user_obj.type not in [0, 1]):
            self.result = unauth_error(message='用户无权限')
            return

        # 添加群组信息
        for user_id in member_list:
            # 判断添加的用户是否存在
            user_obj = self.check_user(user_id)
            # 不存在跳过
            if not user_obj:
                continue

            # 判断用户是否已经在群组中
            group_user_obj = self.check_group_user(group_id, user_id)
            # 存在则跳过
            if group_user_obj:
                continue

            # 存在则添加到群组表中
            group_user_obj = GroupsToUser(group_id=group_id, user_id=user_id)
            db.session.add(group_user_obj)

        if not self.commit(content2='添加异常'):
            return

        self.result = success(message='用户添加成功')

    def put_(self):
        """  修改群成员信息 """
        group_id = self.request_data.get('group_id')
        to_user_id = self.request_data.get('to_user_id')
        remark_name = self.request_data.get('remark_name')
        group_type = self.request_data.get('group_type')  # 成员类型，{0: 群主，1： 管理员， 2：成员}

        # 判断参数是否完整
        if not all([group_id, self.user_id, to_user_id]) or (not remark_name or not group_type):
            self.result = params_error()
            return

        # 判断参数类型是否正确
        if group_type and group_type not in [1, 2] or not isinstance(remark_name, str):
            self.result = params_error(message='参数格式不正确')
            return

        # 修改用户类型，两个用户不能一致
        if group_type and self.user_id == to_user_id:
            self.result = unauth_error(message='权限错误')
            return

        # 检查用户和群组信息是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        group_obj = self.check_group(group_id)
        if not group_obj:
            return

        # 判断目标用户是否存在
        if self.user_id != to_user_id:
            to_user_obj = self.check_user(to_user_id)
            if not to_user_obj:
                return

        # 判断目标用户是否在群组中
        to_group_user_obj = self.check_group_user(to_user_id, group_id)
        if not to_group_user_obj:
            return

        # 修改备注名称
        if remark_name:
            # 判断用户是否有修改权限，如果用户ID不一致，则获取操作用户的权限
            if self.user_id != to_user_id:
                group_user_obj = self.check_group_user(self.user_id, group_id)

                # 用户不为站长，并且用户不在群组中，或者用户不为群主和群管理员
                if user_obj.type != 0 and (not group_user_obj or group_user_obj.type not in [0, 1]):
                    self.result = unauth_error(message='用户无修改权限')
                    return

            # 修改备注名
            to_group_user_obj.remark = remark_name

        # 修改用户权限
        else:
            group_user_obj = self.check_group_user(self.user_id, group_id)

            # 用户不为站长，并且用户不在群组中，或者用户不为群主，或者被修改用户为群主
            if user_obj.type != 0 and (not group_user_obj or group_user_obj.type != 0 or to_group_user_obj.type == 0):
                self.result = unauth_error(message='用户无修改权限')
                return

            # 修改用户权限
            to_group_user_obj.type = group_type

        if not self.commit(content2='群组成员信息修改异常'):
            return

        self.result = success(message='修改成功')

    def delete_(self):
        """  删除群成员信息 """
        print('---------------删除群组成员--------------------')
        print(self.request_data)
        group_id = self.request_data.get('group_id')
        to_user_id = self.request_data.get('to_user_id')

        # 判断参数是否完整
        if not all([group_id, to_user_id]):
            self.result = params_error()

        # 获取用户在群组信息
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 获取被删除用户在群组信息
        to_group_user_obj = self.check_group_user(to_user_id, group_id)
        if not to_group_user_obj:
            return

        # 判断用户是否拥有删除用户权限
        # 用户不为站长，并且用户不在群组中，或者，权限小于目标用户权限
        if self.user_obj.type != 0 and (not group_user_obj or (group_user_obj.type >= to_group_user_obj.type)):
            self.result = unauth_error(message='无修改权限')
            return
        db.session.delete(to_group_user_obj)
        if self.commit():
            self.result = success(message='删除成功')
