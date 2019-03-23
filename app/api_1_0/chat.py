from datetime import datetime
from app import db, redis_store
from app.models import Chat
from utils.restful import params_error, success, unauth_error, server_error
from .common import BaseHandler


class ChatHandler(BaseHandler):
    """  聊天管理 """
    def get_(self):
        if not self.user_obj:
            return

        chat_id = self.request_data.get('chat_id')
        print(self.request_data)
        if chat_id:
            chat = self.check_chat(chat_id)
            if not chat:
                return
            self.result = success(data=chat.to_json())
            return

        if self.user_obj.type == 0:
            chat_obj = self.filter_all(Chat, content='聊天列表查询异常')
        else:
            chat_obj = self.query_(Chat, {'user_id': self.user_id}, '聊天信息获取异常')
        if not chat_obj:
            return

        data_list = []
        for chat in chat_obj:
            chat_data = chat.to_json()
            if chat.type == 1:
                user = self.check_user(chat.chat_obj_id)
                friend = self.check_friend(self.user_id, chat.chat_obj_id)
                if not friend:
                    continue
                chat_data['logo'] = user.logo
                chat_data['name'] = friend.remark or user.nickname

                user_to_user = '_'.join(sorted([str(self.user_id), str(chat.chat_obj_id)]))
                chat_key = 'chat_%s_*' % user_to_user
            else:
                group = self.check_group(chat.chat_obj_id)
                if not group:
                    continue
                print(group)
                chat_data['logo'] = group.logo
                chat_data['name'] = group.name
                chat_key = 'chat_group_%s_*' % chat.chat_obj_id
            keys = redis_store.keys(chat_key)
            keys.sort()
            if keys:
                db_data = eval(redis_store.get(keys[-1]))
                chat_data['message'] = db_data.get('message')
                chat_data['update_time'] = db_data.get('create_time')
            else:
                chat_data['message'] = ''
            data_list.append(chat_data)
        print(data_list)
        data_list = sorted(data_list, key=lambda item: item['update_time'], reverse=True)
        #data_list = [chat.to_json() for chat in chat_obj]
        self.result = success(data=data_list)

    def add_(self):
        """   添加聊天信息  """
        print('add_chat.',self.request_data)
        chat_type = self.request_data.get('chat_type')
        if chat_type == 1:
            name = self.request_data.get('username')
        else:
            name = self.request_data.get('name')

        chat_obj_id = self.request_data.get('id')
        logo = self.request_data.get('logo') or ''

        if not all([name, chat_type, chat_obj_id]) or chat_type not in [1, 2]:
            self.result = params_error()
            return

        if chat_type == 2:
            chat_obj = self.check_group(chat_obj_id)
        else:
            chat_obj = self.check_friend(self.user_id, chat_obj_id)

        if not chat_obj:
            self.result = unauth_error('聊天对象不存在')
            return

        # 判断聊天对象是否存在
        chat = Chat.query.filter_by(user_id=self.user_id, type=chat_type, chat_obj_id=chat_obj_id).first()
        if chat:
            self.result = success(data=chat.id)
            return

        chat = Chat(name=name, type=chat_type, chat_obj_id=chat_obj_id, user_id=self.user_id, logo=logo)
        db.session.add(chat)
        self.commit()
        self.result = success(message='聊天信息添加成功', data=chat.id)

    def delete_(self):
        chat_id = self.request_data.get('chat_id')
        if not chat_id:
            self.result = params_error()
            return

        chat_obj = self.check_chat(chat_id)
        if not chat_obj:
            return

        if not self.user_obj:
            return

        # 判断当前聊天是否属于该用户
        if chat_obj.user_id != self.user_id:
            self.result = unauth_error('用户无权限')
            return

        db.session.delete(chat_obj)
        if not self.commit():
            self.result = server_error('删除异常')
        self.result = success()
