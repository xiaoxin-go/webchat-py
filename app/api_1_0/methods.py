import random
from flask import request, current_app, session
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Group, GroupsToUser, Friends, Chat
from app.constants import DEFAULT_IMAGES
from utils.restful import server_error, params_error, success, unauth_error


class BaseHandler:
    def __init__(self):
        self.result = {}
        self.request_data = {}
        self.user_id = session.get('id')

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
        return group_user_obj

    def check_friend(self, user_id, friend_id):
        """  检查好友信息是否存在 """
        try:
            friend_obj = Friends.qeury.filter_by(user_id=user_id, friend_id=friend_id).first()
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
            query_obj = obj.query.all()
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
        return True


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
        if not all([username, password]):
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


class GroupHandler(BaseHandler):
    """ 群组操作 """

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
                self.result = server_error(message='群组查询异常')
                return
        else:
            group_query = self.filter_all(Group, content='群组查询异常')

        # 分页
        group_obj = group_query.paginate(page=page, per_page=page_size, error_out=False)
        # 对象转换成列表
        group_list = [group.to_dict() for group in group_obj.items]
        total = group_query.count()

        self.result = success(data=group_list)

    def add_(self):
        """  添加群组信息 """

        group_name = self.request_data.get('group_name')
        if not all([self.user_id, group_name]):
            self.result = params_error()
            return

        # 获取用户，判断用户类型是否正确
        user_obj = self.check_user()
        if not user_obj or user_obj.type not in [0, 1]:
            self.result = unauth_error(message='用户无权限')
            return

        # 设置群组头像，随机从默认图片中选取一张做为头像
        group_logo = self.request_data.get('logo')
        if not group_logo:
            group_logo = random.choice(DEFAULT_IMAGES)

        # 添加群组
        group_obj = Group(group_name=group_name, logo=group_logo)
        db.session.add(group_obj)
        if not self.commit('群组已存在', '群组添加异常'):
            return

        group_info = self.request_data.get('info')  # 获取群公告信息
        # 添加群组
        group_to_user = GroupsToUser(group_id=group_obj.id, user_id=self.user_id, type=0, group_info=group_info)
        db.session.add(group_to_user)
        if not self.commit(content2='群组添加异常'):
            return

        self.result = success(message='群组添加成功')

    def put_(self):
        """  修改群组信息，群组名称，头像 """
        group_id = self.request_data.get('group_id')
        group_logo = self.request_data.get('group_logo')
        group_name = self.request_data.get('group_name')
        group_info = self.request_data.get('group_info')

        # 用户ID和群组ID必须存在，并且群组名和群组头像至少存在一项
        if not all([group_id, self.user_id]) or (
                all([group_id, self.user_id]) and (not group_logo and not group_name and not group_info)):
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
        if group_name:
            group_obj.group_name = group_name
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
        if not all([group_id, self.user_id]):
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

        # 判断用户是否为站长，或者是否为群主
        if user_obj.type != 0 and (not group_user_obj or group_user_obj.type != 0):
            self.result = unauth_error(message='用户无权限')
            return

        # 删除群组信息
        db.session.delete(group_obj)
        group_user_query = self.query_(GroupsToUser, {'group_id': group_id}, '群组成员信息查询异常')
        if not group_user_query:
            return
        group_user_query.delete()

        if not self.commit(content2='群组信息修改异常'):
            return

        self.result = success(message='群组修改成功')


class GroupUserHandler(BaseHandler):
    """  群成员操作 """

    def get_(self):
        """  获取群成员信息 """
        group_id = self.request_data.get('group_id')
        if not all([group_id, self.user_id]):
            self.result = params_error()
            return

        # 检查群组是否存在
        group_obj = self.check_group(group_id)
        if not group_obj:
            return

        # 检查用户是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        # 获取成员是否在群组中
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 判断用户是否拥有添加成员权限，判断是否为站长，或者是否为群主或群管理员
        if user_obj.type != 0 and not group_user_obj:
            self.result = unauth_error(message='用户无权限')
            return

        # 获取成员列表
        group_user_query = self.query_(GroupsToUser, {'group_id': group_id}, '群组成员获取异常')
        if not group_user_query:
            return

        data_list = [group_user.to_dict for group_user in group_user_query]
        total = group_user_query.count()
        self.result = success(data=data_list)

    def add_(self):
        """  添加群成员 """
        group_id = self.request_data.get('group_id')
        member_list = self.request_data.get('member_list')

        # 判断参数是否完整
        if not all([group_id, self.user_id, member_list]):
            self.result = params_error()
            return

        # 检查群组是否存在
        group_obj = self.check_group(group_id)
        if not group_obj:
            return

        # 检查用户是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        # 获取成员是否在群组中
        group_user_obj = self.check_group_user(self.user_id, group_id)

        # 判断用户是否拥有添加成员权限，判断是否为站长，或者是否为群主或群管理员
        if user_obj.type != 0 and (not group_user_obj or group_user_obj.type not in [0, 1]):
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
        group_id = self.request_data.get('group_id')
        to_user_id = self.request_data.get('to_user_id')

        # 判断参数是否完整
        if not all([group_id, self.user_id, to_user_id]):
            self.result = params_error()

        # 检查用户和群组信息是否存在
        check_obj = self.check_group_user(self.user_id, group_id)
        if not check_obj:
            return

        user_obj, group_obj, group_user_obj = check_obj

        # 判断目标用户是否存在
        if self.user_id != to_user_id:
            to_user_obj = self.check_user(to_user_id)
            if not to_user_obj:
                self.result = server_error(message='用户信息不存在')
                return

        # 判断目标用户是否在群组中
        to_group_user_obj = self.check_group_user(to_user_id, group_id)

        if not to_group_user_obj:
            self.result = unauth_error(message='目标用户不在群组中')
            return

        # 判断用户是否拥有删除用户权限
        # 用户不为站长，并且用户不在群组中，或者，权限小于目标用户权限
        if user_obj.type != 0 and (not group_user_obj or (group_user_obj.type >= to_group_user_obj.type)):
            self.result = unauth_error(message='无修改权限')
            return

        db.session.delete(to_group_user_obj)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            self.result = server_error(message='删除异常')
            return
        self.result = success(message='删除成功')


class FriendHandler(BaseHandler):
    """  好友管理 """

    def get_(self):
        """  获取好友列表 """
        # 判断用户是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        # 获取好友信息
        friends_query = self.query_(Friends, {'user_id', self.user_id}, '好友信息查询异常')
        if not friends_query:
            return
        friend_list = [friend.id for friend in friends_query]
        data_list = [User.query.get(user_id).to_dict for user_id in friend_list]
        self.result = success(data=data_list)

    def add_(self):
        """  添加好友，只有副站长和管理员拥有加人权限，强制添加，不需要同意 """

        # 判断用户是否存在，获取用户
        user_obj = self.check_user()
        if not user_obj:
            return

        friend_id = self.request_data.get('friend_id')
        if not friend_id:
            self.result = params_error()
            return
        # 判断被添加用户是否存在
        to_user_obj = self.check_user(friend_id)
        if not to_user_obj:
            return

        # 获取群ID
        group_id = self.request_data.get('group_id')
        group_user_obj = self.check_group_user(self.user_id, group_id)

        if user_obj.type in [0, 1] or (group_user_obj and group_user_obj.type in [0, 1]):
            self.add_handler(self.user_id, friend_id)
        else:
            self.result = unauth_error(message='无添加权限')

    def put_(self):
        """  修改好友信息，备注信息 """
        friend_id = self.request_data.get('friend_id')
        remark = self.request_data.get('remark')
        if not all([friend_id, remark]):
            self.result = params_error()
            return

        # 检查用户是否存在
        user_obj = self.check_user()
        if not user_obj:
            return

        friend_obj = self.check_friend(self.user_id, friend_id)
        if not friend_id:
            return

        friend_obj.remark = remark
        self.commit()
        self.result = success(message='好友备注修改成功')

    def delete_(self):
        """  删除好友 """
        friend_id = self.request_data.get('friend_id')
        if not friend_id:
            self.result = params_error()
            return

        if not self.check_user():
            return

        friend_obj = self.check_friend(self.user_id, friend_id)
        if not friend_obj:
            return

        friend_obj.delete()
        self.commit()
        self.result = success(message='好友删除成功')

    def add_handler(self, user_id, friend_id):
        """   添加好友方法 """
        friend_obj = Friends(user_id=user_id, friend_id=friend_id)
        friend_obj_to = Friends(user_id=friend_id, friend_id=user_id)
        db.session.add(friend_obj)
        db.session.add(friend_obj_to)
        self.commit()
        self.result = success(message='好友添加成功')


class ChatHandler(BaseHandler):
    """  聊天管理 """
    def get_(self):
        user_obj = self.check_user()
        if not user_obj:
            return

        chat_obj = self.filter_all(Chat, content='聊天列表查询异常')
        if not chat_obj:
            return

        data_list = [chat.to_json() for chat in chat_obj]
        self.result = success(data=data_list)

    def add_(self):
        """   添加聊天信息  """
        name = self.request_data.get('name')
        chat_type = self.request_data.get('type')
        chat_obj_id = self.request_data.get('chat_obj_id')
        logo = self.request_data.get('logo')

        if not all([name, chat_type, chat_obj_id, logo]) or chat_type not in ['group', 'friend']:
            self.result = params_error()
            return

        if chat_type == 'group':
            chat_obj = self.check_group(chat_obj_id)
        else:
            chat_obj = self.check_friend(self.user_id, chat_obj_id)

        if not chat_obj:
            self.result = unauth_error('聊天对象不存在')
            return

        chat = Chat(name=name, type=chat_type, chat_obj_id=chat_obj_id, user_id=self.user_id, logo=logo)
        db.session.add(chat)
        self.commit()
        self.result = success(message='聊天信息添加成功')

    def delete_(self):
        chat_id = self.request_data.get('chat_id')
        if not chat_id:
            self.result = params_error()
            return

        chat_obj = self.check_chat(chat_id)
        if not chat_obj:
            return

        user_obj = self.check_user()
        if not user_obj:
            return

        # 判断当前聊天是否属于该用户
        if chat_obj.user_id != self.user_id:
            self.result = unauth_error('用户无权限')
            return

        chat_obj.delete()
        self.commit()


class ChatMessageHandler(BaseHandler):
    def get_(self):
        """  获取聊天记录，建议保存到缓存数据库中，以用户的聊天为ID为ID  """
        pass