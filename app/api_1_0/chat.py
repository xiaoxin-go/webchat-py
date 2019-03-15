from datetime import datetime
from app import db
from app.models import Chat
from utils.restful import params_error, success, unauth_error
from .common import BaseHandler


class ChatHandler(BaseHandler):
    """  聊天管理 """
    def get_(self):
        if not self.user_obj:
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

        # 判断聊天对象是否存在
        chat = Chat.query.filter_by(user_id=self.user_id, type=chat_type, chat_obj_id=chat_obj_id).first()
        if chat:
            chat.update_time = datetime.now()
            self.commit()
            self.result = success(data=chat.to_json())
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

        if not self.user_obj:
            return

        # 判断当前聊天是否属于该用户
        if chat_obj.user_id != self.user_id:
            self.result = unauth_error('用户无权限')
            return

        chat_obj.delete()
        self.commit()
