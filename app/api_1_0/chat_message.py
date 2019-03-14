from app import redis_store
from utils.restful import success
from .common import BaseHandler


class ChatMessageHandler(BaseHandler):
    def get_(self):
        """  获取聊天记录，建议保存到缓存数据库中，以用户的聊天为ID为ID  """
        # 从缓存数据库获取聊天记录，根据ID + 产生时间为key
        # '1-add_time' = {'message': 消息内容, 'add_time': '添加时间', 'user_id': '发送的用户ID'}
        chat_id = self.request_data.get('chat_id')
        chat_keys = redis_store.keys('%s_*' % chat_id)
        data_list = []
        for chat_key in chat_keys:
            message = redis_store.get(chat_key)
            data_list.append(message)

        self.result = success(data=data_list)