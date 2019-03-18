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

        # 如果chat.type为1，则是单聊，取chat_user_touser_*
        if chat.type == 1:
            user_to_user = '_'.join(sorted([str(chat.user_id), str(chat.chat_obj_id)]))
            chat_keys = redis_store.keys('chat_%s_*' % user_to_user)
        # 否则为群组聊天，取chat_group_groupid
        else:
            chat_keys = redis_store.keys('chat_group_%s_*' % chat.chat_obj_id)
        chat_keys.sort()
        print('---------输出聊天keys和记录-------------------------')
        print(chat_keys)

        data_list = []
        for chat_key in chat_keys:
            message = redis_store.get(chat_key)
            try:
                data_list.append(eval(message))
            except Exception as e:
                continue
        print(data_list)
        print('-------------end-----------------------')
        self.result = success(data=data_list)