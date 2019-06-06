from app import redis_store
from utils.restful import success
from .common import BaseHandler

import json


class ChatMessageHandler(BaseHandler):
    def get_(self):
        """  获取聊天记录，建议保存到缓存数据库中，以用户的聊天为ID为ID  """
        # 从缓存数据库获取聊天记录，根据ID + 产生时间为key
        # '1-add_time' = {'message': 消息内容, 'add_time': '添加时间', 'user_id': '发送的用户ID'}
        print('获取数据：', self.request_data)
        chat_id = self.request_data.get('chat_id')
        chat = self.check_chat(chat_id)
        if not chat:
            return

        chat_key = chat.chat_key
        print('---------输出聊天keys和记录-------------------------')

        t = self.request_data.get('t')
        if not t:
            chat_keys = redis_store.zrevrange(chat_key, 0, 19)
        else:
            chat_keys = redis_store.zrangebyscore(chat_key, t - 20, t)

        data_list = [eval(data) for data in redis_store.mget(chat_keys)]
        print(data_list)
        print('-------------end-----------------------')
        self.result = success(data=data_list)