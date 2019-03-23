from flask_socketio import emit
from flask import session
from app.models import Chat, GroupsToUser
from app.api_1_0.common import now, BaseHandler
from app import db, redis_store


class SendMessage(BaseHandler):
    def __init__(self, request_data):
        request_data = request_data
        self.user_data = request_data.get('user_data')
        self.user_id = self.user_data.get('id')
        print('输出用户发出的消息-----------------------')
        print(request_data)

        self.add_time = now()

        # 获取用户发送的消息，和chat信息
        self.message = request_data.get('message')
        self.user_data['message'] = self.message
        self.user_data['add_time'] = self.add_time

        self.chat = request_data.get('chat')
        self.chat_obj_id = self.chat.get('chat_obj_id')

        chat_type = self.chat.get('type')
        if chat_type not in [1, 2]:
            print('聊天类型不正确')
            return

        if chat_type == 1:
            self.one_to_one()
        else:
            self.group_chat()

    def one_to_one(self):
        """
        单聊发送消息模式
        1. 获取用户发送的消息，用户信息，聊天ID，聊天对象ID
        2. 获取对方聊天ID，若对方聊天ID不存在，则创建
        3. 更新用户的聊天信息，将聊天信息加入到双方聊天信息中, chat_user_id_to_user_id
        4. 获取用户聊天对象的SID，发送消息给对方
        """
        # 判断对方聊天信息是否存在， 若不存在则创建
        to_chat_data= self.add_chat(user_id=self.chat_obj_id, chat_type=1, chat_obj_id=self.user_id)

        # 对方用户ID进行排序，用以保存聊天记录
        user_to_user = '_'.join(sorted([str(self.user_id), str(self.chat_obj_id)]))
        chat_key = 'chat_%s_%s' % (user_to_user, self.add_time)
        # 聊天记录保存两天
        redis_store.set(chat_key, self.user_data, 3600 * 48)
        print('用户单聊。。。。。。。。。')
        # 获取对方用户SID，发送消息给对方
        sid_key = 'chat_sid_%s' % self.chat_obj_id
        obj_sid = redis_store.get(sid_key)
        print(obj_sid)
        if obj_sid:
            result_data = {
                'user_data': self.user_data,
                'chat_data': to_chat_data
            }
            print(result_data)
            emit('response',result_data, room=obj_sid.decode())

    def group_chat(self):
        """
        群聊模式发送消息
        1. 获取用户发送的消息，用户信息，聊天ID，聊天对象ID
        2. 更新用户聊天信息，将聊天信息加入到群组聊天中，chat_group_group_id_now
        3. 获取群组所有成员SID，发送消息给对方
        """
        # 保存群聊消息
        chat_key = 'chat_group_%s_%s' % (self.chat_obj_id, self.add_time)
        redis_store.set(chat_key, self.user_data, 3600*48)

        print('群聊。。。。。。。。。')
        # 获取群用户消息
        group_user_query = GroupsToUser.query.filter_by(group_id=self.chat_obj_id)
        for group_user in group_user_query:
            # 如果是当前用户则跳过
            if group_user.user_id == self.user_id:
                continue

            # 根据群成员ID，判断对方当前群聊天是否存在，获取聊天data
            to_chat_data = self.add_chat(user_id=group_user.user_id, chat_type=2, chat_obj_id=self.chat_obj_id)

            # 获取用户SID，判断SID是否存在，若存在则发送消息
            sid_key = 'chat_sid_%s' % group_user.user_id
            obj_sid = redis_store.get(sid_key)
            print(obj_sid)
            if obj_sid:
                result_data = {
                    'user_data': self.user_data,
                    'chat_data': to_chat_data
                }
                print(result_data)
                emit('response', result_data, room=obj_sid.decode())

    def add_chat(self, user_id, chat_obj_id, chat_type):
        """
        判断聊天对象是否存在，若不存在则创建
        """
        chat_obj = Chat.query.filter_by(user_id=user_id, chat_obj_id=chat_obj_id, type=chat_type).first()
        if not chat_obj:
            chat_obj = Chat(user_id=user_id, chat_obj_id=chat_obj_id, type=chat_type)
            db.session.add(chat_obj)
            db.session.commit()
            chat_id = chat_obj.id
        chat_data = chat_obj.to_json()
        if chat_type == 1:
            # 获取用户头像和昵称
            friend = self.check_friend(friend_id=self.user_id, user_id=chat_obj_id)
            if friend:
                chat_data['name'] = friend.remark or self.user_data.get('nickname')

            chat_data['logo'] = self.user_data.get('logo')
        else:
            group = self.check_group(chat_obj_id)
            chat_data['name'] = group.name
            chat_data['logo'] = group.logo

        chat_data['message'] = self.message
        chat_data['update_time'] = self.add_time
        return chat_data