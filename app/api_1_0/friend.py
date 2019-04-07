from app import db
from app.models import Friends
from utils.restful import params_error, success, unauth_error
from .common import BaseHandler


class FriendHandler(BaseHandler):
    """  好友管理 """

    def get_(self):
        """  获取好友列表 """
        # 获取好友信息
        if self.user_obj.type == 0:
            friends_query = self.filter_all(Friends, '好友信息查询异常')
        else:
            friends_query = self.query_(Friends, {'user_id': self.user_id}, '好友信息查询异常')
        if not friends_query:
            return

        data_list = []
        for friend in friends_query:
            user_obj = self.check_user(friend.friend_id)
            if not user_obj:
                continue
            user_info = user_obj.to_dict()
            user_info['remark_name'] = friend.remark
            data_list.append(user_info)
        self.result = success(data=data_list)

    def add_(self):
        """  添加好友，只有副站长和管理员拥有加人权限，强制添加，不需要同意 """

        friend_id = self.request_data.get('friend_id')
        if not friend_id:
            self.result = params_error()
            return

        # 判断被添加用户是否存在
        to_user_obj = self.check_user(friend_id)
        if not to_user_obj:
            return

        # 判断是否已经是好友
        friend_user = self.check_friend(self.user_id, friend_id)
        if friend_user:
            self.result = params_error(message='已是好友')
            return

        # 获取群ID
        # group_id = self.request_data.get('group_id')
        # group_user_obj = self.check_group_user(self.user_id, group_id)

        # if self.user_obj.type in [0, 1] or (group_user_obj and group_user_obj.type in [0, 1]):
        self.add_handler(self.user_id, friend_id)
        # else:
        #     self.result = unauth_error(message='无添加权限')

    def put_(self):
        """  修改好友信息，备注信息 """
        friend_id = self.request_data.get('friend_id')
        remark = self.request_data.get('remark')
        if not all([friend_id, remark]):
            self.result = params_error()
            return

        friend_obj = self.check_friend(self.user_id, friend_id)
        if not friend_obj:
            return

        friend_obj.remark = remark
        if not self.commit():
            return
        self.result = success(message='好友备注修改成功')

    def delete_(self):
        """  删除好友 """
        friend_id = self.request_data.get('friend_id')
        if not friend_id:
            self.result = params_error()
            return

        friend_obj = self.check_friend(self.user_id, friend_id)
        if not friend_obj:
            return

        friend_obj_to = self.check_friend(friend_id, self.user_id)
        if friend_obj_to == 400:
            return

        db.session.delete(friend_obj)
        #db.session.delete(friend_obj_to)
        if not self.commit():
            return
        self.result = success(message='好友删除成功')

    def add_handler(self, user_id, friend_id):
        """   添加好友方法 """
        friend_obj = Friends(user_id=user_id, friend_id=friend_id)
        friend_obj_to = Friends(user_id=friend_id, friend_id=user_id)
        db.session.add(friend_obj)
        db.session.add(friend_obj_to)
        if not self.commit(): return
        self.result = success(message='好友添加成功')


class FriendInfoHandler(BaseHandler):
    def get_(self):
        friend_id = self.request_data.get('friend_id')
        user_obj = self.check_user(friend_id)
        if not user_obj:
            return

        friend_obj = self.check_friend(self.user_id, friend_id)
        if not friend_obj:
            return
        user_data = user_obj.to_dict()
        user_data['remark'] = friend_obj.remark
        self.result = success(data=user_data)
