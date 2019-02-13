import random
from flask import request, current_app
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Group, GroupsToUser
from app.constants import DEFAULT_IMAGES


class BaseHandler:
    def __init__(self):
        self.result = {}
        self.request_data = {}

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


class GroupHandler(BaseHandler):
    def get_(self):
        """  获取群组信息 """
        page = self.request_data.get('page') or 1
        page_size = self.request_data.get('page_size') or 10
        keyword = self.request_data.get('keyword') or ''
        if keyword:
            try:
                group_query = Group.query.filter(Group.group_name.like("%{}%".format(keyword)))
            except Exception as e:
                current_app.logger.error(e)
                self.result = {'state': 2, 'message': '群组查询异常'}
                return
        else:
            try:
                group_query = Group.query.filter()
            except Exception as e:
                current_app.logger.error(e)
                self.result = {'state': 2, 'message': '群组查询异常'}
                return

        # 分页
        group_obj = group_query.paginate(page=page, per_page=page_size, error_out=False)
        # 对象转换成列表
        group_list = [group.to_dict() for group in group_obj.items]
        total = group_query.count()

        self.result = {'state': 1, 'data_list': group_list, 'total': total}

    def add_(self):
        """  添加群组信息 """

        user_id = self.request_data.get('user_id')
        group_name = self.request_data.get('group_name')
        if not all([user_id, group_name]):
            self.result = {'state': 2, 'message': '缺少必要参数'}
            return

        # 获取用户，判断用户类型是否正确
        user_obj = User.query.get(user_id)
        if not user_obj or user_obj.type not in [0, 1]:
            self.result = {'state': 2, 'message': '用户类型错误'}
            return

        group_logo = self.request_data.get('logo')
        if not group_logo:
            group_logo = random.choice(DEFAULT_IMAGES)

        # 添加群组
        group_obj = Group(group_name=group_name, logo=group_logo)
        try:
            db.session.add(group_obj)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '群组已存在'}
            return
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '群组添加异常'}

        # 添加群组
        group_to_user = GroupsToUser(group_id=group_obj.id, user_id=user_id, type=0)
        db.session.add(group_to_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '群组添加异常'}
            return

        self.result = {'state': 1, 'message': '群组添加成功'}

    def put_(self):
        """  修改群组信息，群组名称，头像 """
        group_id = self.request_data.get('group_id')
        user_id = self.request_data.get('user_id')
        group_logo = self.request_data.get('group_logo')
        group_name = self.request_data.get('group_name')

        # 用户ID和群组ID必须存在，并且群组名和群组头像至少存在一项
        if not all([group_id, user_id]) or (all([group_id, user_id]) and (not group_logo and not group_name)):
            self.result = {'state': 2, 'message': '缺失必要参数'}
            return

        # 获取群组信息，判断群组是否存在
        try:
            group_obj = Group.query.get(group_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '群组查询异常'}
            return

        if not group_obj:
            self.result = {'state': 2, 'message': '群组信息不存在'}
            return

        # 获取用户信息，判断用户是否存在
        try:
            user_obj = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '用户信息查询异常'}
            return

        if not user_obj:
            self.result = {'state': 2, 'message': '用户信息不存在'}
            return

        # 判断用户是否有修改群组权限
        try:
            group_user_obj = GroupsToUser.query.filter_by(user_id=user_id, group_id=group_id).first()
        except Exception as e:
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '群组成员信息查询异常'}
            return

        # 用户不在群组中并且用户非站长， 或者用户在群组中非管理员
        if user_obj.type != 0 and (not group_user_obj or group_user_obj.type not in [0, 1]):
            self.result = {'state': 2, 'message': '用户无修改群组权限'}
            return

        # 修改群组信息
        if group_name:
            group_obj.group_name = group_name
        if group_logo:
            group_obj.logo = group_logo

        try:
            db.session.commit()
        except IntegrityError as e:
            current_app.logger.error(e)
            db.session.rollback()
            self.result = {'state': 2, 'message': '群组名已存在'}
            return
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            self.result = {'state': 2, 'message': '群组修改异常'}
            return

        self.result = {'state': 1, 'message': '群组信息修改成功'}

    def delete_(self):
        """  删除群组 """
        group_id = self.request_data.get('group_id')
        user_id = self.request_data.get('user_id')

        # 判断参数是否完整
        if not all([group_id, user_id]):
            self.result = {'state': 2, 'message': '缺少必要参数'}
            return

        # 获取群组信息
        try:
            group_obj = Group.query.get(group_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '获取群组异常'}
            return

        if not group_obj:
            self.result = {'state': 2, 'message': '群组不存在'}
            return

        # 获取用户信息
        try:
            user_obj = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '获取用户信息异常'}
            return

        if not user_obj:
            self.result = {'state': 2, 'message': '用户信息不存在'}
            return

        # 获取群组成员信息
        try:
            group_user_obj = GroupsToUser.query.filter_by(group_id=group_id, user_id=user_id).first()
        except Exception as e:
            current_app.logger.error(e)
            self.result = {'state': 2, 'message': '获取群组用户信息异常'}
            return

        # 判断用户是否为站长，或者是否为群主
        if user_obj.type != 0 and (not group_user_obj or group_user_obj.type != 0):
            self.result = {'state': 2, 'message': '用户无此权限'}
            return

        # 删除群组信息
        db.session.delete(group_obj)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            self.result = {'state': 2, 'message': '群组信息删除异常'}
            return

        try:
            GroupsToUser.query.filter_by(group_id=group_id).delete()
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            self.result = {'state': 2, 'message': '群组信息删除异常'}
            return

        self.result = {'state': 1, 'message': '群组信息删除成功'}
