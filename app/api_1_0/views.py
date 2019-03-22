from . import bp
from flask import request, jsonify, current_app, session, render_template, redirect, url_for
from flask_socketio import emit
from app import redis_store, socketio
from .chat import ChatHandler
from .user import UserHandler, UserInfoHandler
from .group import GroupHandler
from .group_user import GroupUserHandler
from .friend import FriendHandler
from .chat_message import ChatMessageHandler
from utils.restful import server_error, params_error, success, unauth_error
from utils.cut_image import CutImage
from app.models import *
from .common import now

import time
import uuid
import json


def ack(value):
    print(value)


@socketio.on('message')
def handle_json(request_data):
    # 获取发送的数据
    user_id = session.get('id')
    user_data = request_data.get('user_data')
    chat_id = request_data.get('chat_id')
    message = request_data.get('message')
    print('-----------------------输出用户发出的消息--------------------')
    print(request_data)
    print('------------------------end------------------------')
    # 获取聊天信息，并将发送的数据保存到redis中，并更新聊天信息
    user_data['message'] = message
    user_data['add_time'] = now()
    chat_obj = Chat.query.get(chat_id)
    print('-------------------------打印聊天类型----------------')
    print('chat_obj.type',chat_obj.type)

    chat_obj.message = message
    chat_obj.update_time = now()

    # 发送消息，获取聊天类型，如果是1，则是单聊
    # 获取聊天对象ID，获取此聊天的sid，向此用户发送消息
    chat_obj_id = chat_obj.chat_obj_id
    if chat_obj.type == 1:
        # 获取对方chat_id，并更新对方聊天记录，若聊天不存在，则创建
        to_chat_obj = Chat.query.filter_by(user_id=chat_obj_id, chat_obj_id=user_id).first()
        if not to_chat_obj:
            to_chat_obj = Chat(user_id=chat_obj_id, type=1, chat_obj_id=user_id, message=message, logo=user_data.get('logo'), name=user_data.get('nickname'))
            db.session.add(to_chat_obj)
            db.session.commit()
            print(to_chat_obj.id)
        else:
            to_chat_obj.message = message
            to_chat_obj.update_time = now()

        # 若是单聊，保存聊天消息，为chat_user_to_user
        user_to_user = '_'.join(sorted([str(user_id), str(chat_obj_id)]))
        chat_key = 'chat_%s_%s' % (user_to_user, now())
        redis_store.set(chat_key, user_data, 3600 * 24)

        # 获取对方用户聊天SID，若sid存在，则证明对方用户在聊天室中，则发送消息给对方
        chat_key = 'chat_sid_%s_%s' % (user_to_user, chat_obj_id)
        chat_sid = redis_store.get(chat_key)
        print('-----------打印对方SID--------------')
        print(chat_key, chat_sid)
        print('-----------end---------------')
        if chat_sid:
            emit('message', user_data, room=chat_sid.decode())

        # 获取对方chat_list_sid，若sid存在，则证明对方在聊天列表页面，发送消息给对方
        chat_list_key = 'chat_list_sid_%s' % chat_obj_id
        print('-----------打印chat_list_sid------------')
        chat_list_sid = redis_store.get(chat_list_key)
        print(chat_list_sid)
        print('------------end------------------')
        if chat_list_sid:
            emit('message', to_chat_obj.to_json(), room=chat_list_sid.decode())

    # 否则为群组聊天，获取聊天对象ID
    else:
        # 若是群聊，保存聊天消息，为chat_group_group_id
        chat_key = 'chat_group_%s_%s' % (chat_obj_id, now())
        redis_store.set(chat_key, user_data, 3600 * 24)

        # 获取当前群组成员
        group_user_query = GroupsToUser.query.filter_by(group_id=chat_obj_id)
        for group_user in group_user_query:
            # 如果用户为当前用户则跳过
            if group_user.user_id == user_id:
                continue

            # 获取对方chat_id，并更新对方聊天记录，若聊天不存在，则创建
            to_chat_obj = Chat.query.filter_by(user_id=group_user.user_id, chat_obj_id=chat_obj_id).first()
            if not to_chat_obj:
                to_chat_obj = Chat(user_id=group_user.user_id, type=1, chat_obj_id=chat_obj_id, message=message, logo=chat_obj.logo)
                db.session.add(to_chat_obj)
                db.session.commit()
                print(to_chat_obj.id)
            else:
                to_chat_obj.message = message
                to_chat_obj.update_time = now()

            chat_key = 'chat_sid_%s_%s' % (chat_obj_id, group_user.user_id)
            chat_sid = redis_store.get(chat_key)
            print('--------------打印群组用户SID-------------')
            print('chat_key', chat_key, chat_sid)
            print('--------------end------------------')
            # 如果用户ID存在
            if chat_sid:
                emit('message', user_data, room=chat_sid.decode())

            chat_list_key = 'chat_list_sid_%s' % group_user.user_id
            chat_list_sid = redis_store.get(chat_list_key)
            print('--------------打印群组用户列表SID-------------')
            print('chat_list_key', chat_list_key, chat_list_sid)
            print('--------------end------------------')
            if chat_list_sid:
                emit('message', to_chat_obj.to_json(), room=chat_list_sid.decode())

    db.session.commit()


@socketio.on('in_chat')
def in_chat(chat):
    """
    用户进入聊天页面，将用户的id和sid绑定，为chat_chatid_sid_userid = sid
    :return:
    """
    print('---------------用户进入聊天页面---------------')
    print(chat, request.sid)
    print(session.get('nickname'))
    print('---------------end---------------')
    if not chat:
        return
    sid = request.sid
    user_id = session.get('id')
    # 获取聊天类型，若为1,则为单聊，组合聊天对象，设置用户聊天ID chat_sid_usertouserid_userid
    chat_obj_id = chat['chat_obj_id']
    chat_type = chat.get('type')
    if chat_type not in [1, 2]:
        return
    if chat_type == 1:
        user_to_user = '_'.join(sorted([str(user_id), str(chat_obj_id)]))
        chat_key = 'chat_sid_%s_%s' % (user_to_user, user_id)

    # 否则聊天类型为群组，设置为群组加用户ID chat_sid_groupid_userid
    else:
        chat_key = 'chat_sid_%s_%s' % (chat_obj_id, user_id)
    redis_store.set(chat_key, sid, 3600*12)
    #emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('out_chat')
def out_chat(chat):
    """
    用户退出聊天界面，删除用户的sid
    :return:
    """
    if not chat:
        return
    print('-----------------用户退出聊天页面----------------')
    print(chat)
    print(session.get('nickname'))
    print('-----------------end-------------------')
    user_id = session.get('id')
    # 获取聊天类型，若为1,则为单聊，组合聊天对象，设置用户聊天ID chat_sid_usertouserid_userid
    chat_obj_id = chat['chat_obj_id']
    chat_type = chat.get('type')
    if chat_type not in [1, 2]:
        return
    if chat_type == 1:
        user_to_user = '_'.join(sorted([str(user_id), str(chat_obj_id)]))
        chat_key = 'chat_sid_%s_%s' % (user_to_user, user_id)

    # 否则聊天类型为群组，设置为群组加用户ID chat_sid_groupid_userid
    else:
        chat_key = 'chat_sid_%s_%s' % (chat_obj_id, user_id)
    redis_store.delete(chat_key)
    #emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('in_chat_list')
def in_chat_list():
    """
    用户进入聊天列表，将用户的id和sid绑定，为chat_list_sid_userid = sid
    :return:
    """
    print('---------------用户进入聊天列表-----------------')
    sid = request.sid
    user_id = session.get('id')
    print(user_id, session.get('nickname'), sid)
    print('---------------end-----------------')
    chat_key = 'chat_list_sid_%s' % user_id
    redis_store.set(chat_key, sid, 3600*12)
    #emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('out_chat_list')
def out_chat_list():
    """
    退出聊天列表，清除用户sid
    :return:
    """
    print('---------------用户退出聊天列表-----------------')
    print(session.get('nickname'))
    print('---------------end-----------------')
    user_id = session.get('id')
    chat_key = 'chat_list_sid_%s' % user_id
    redis_store.delete(chat_key)
    #emit('message', 'test', room=request.sid, callback=ack)


@bp.route('/user_info', methods=['GET'])
def user_info():
    user_handler = UserInfoHandler()
    return jsonify(user_handler.result)


@bp.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    """  用户管理  """
    user_handler = UserHandler()
    return jsonify(user_handler.result)


@bp.route('/', methods=['GET'])
def index():
    #if session.get('id'):
    return render_template('index.html')

    #login_url = url_for('.login', _external=True)
    #return redirect(login_url)


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    用户名、 密码
    :return:
    """
    #index_url = url_for('.index', _external=True)

    #if session.get('id'):
    #    return redirect(index_url)

    #if request.method == 'GET':
    #    return render_template('login.html')


    # 获取用户传输数据
    request_data = request.json
    username = request_data.get('username')
    password = request_data.get('password')

    if not all([username, password]):
        #return render_template('login.html', message='缺少必要参数')
        return jsonify(params_error(message='缺少必要参数'))

    # 获取用户登录IP
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums and int(access_nums) >= 5:
            #return render_template('login.html', message='错误次数过多，请稍后重试')
            return jsonify(unauth_error(message='错误次数过多，请稍后重试'))

    # 从数据库查询用户对象
    try:
        user_obj = User.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        #return render_template('login.html', message='获取用户信息失败')
        return jsonify(server_error(message = '获取用户信息失败'))

    # 取出用户密码与数据库密码对比
    if not user_obj or not user_obj.check_password(password):
        # 如果用户不存在或者用户密码不正确，返回错误消息，并记录错误次数
        try:
            # redis的incr可以对字符串类型数据进行加1操作，如果数据开始不存在，则默认设置为1
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, 600)  # 数据保存600秒
        except Exception as e:
            current_app.logger.error(e)
        #return render_template('login.html', message='用户名或密码错误')
        return jsonify(unauth_error(message='用户名或密码错误'))

    # 登录成功
    session['username'] = username
    session['nickname'] = user_obj.nickname
    session['id'] = user_obj.id

    # 更改用户在线状态
    user_obj.state = 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        #return render_template('login.html', message='登录异常')
        return jsonify(server_error('登录异常'))

    #return redirect(index_url)
    return jsonify(success(data=user_obj.to_dict(), message='用户登录成功'))


@bp.route('/check_login', methods=['GET'])
def check_login():
    """
    检查用户是否登录
    :return:
    """
    user_id = session.get('id')
    print('用户ID：',user_id)
    if not user_id:
        return jsonify(unauth_error(message='用户未登录'))

    user_obj = User.query.filter_by(id=user_id).first()
    if not user_obj:
        return jsonify(unauth_error(message='用户不存在'))

    # 返回已登录状态，和用户数据
    return jsonify(success(data=user_obj.to_dict()))


@bp.route('/logout', methods=['POST'])
def logout():
    """ 用户退出登录 """
    id = session.get('id')
    try:
        user_obj = User.query.get(id)
        user_obj.state = 0
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
    session.clear()     # 清除用户session
    return jsonify(success())


@bp.route('/group', methods=['GET', 'POST', 'PUT', 'DELETE'])
def group():
    """  群组管理 """
    group_handler = GroupHandler()
    return jsonify(group_handler.result)


@bp.route('/group_user', methods=['GET','POST', 'PUT', 'DELETE'])
def group_user():
    """  群组成员管理 """
    group_user_handler = GroupUserHandler()
    return jsonify(group_user_handler.result)


@bp.route('/friend', methods=['GET', 'POST', 'PUT', 'DELETE'])
def friend():
    """  好友管理 """
    friend_handler = FriendHandler()
    return jsonify(friend_handler.result)


@bp.route('/chat', methods=['GET', 'POST', 'DELETE'])
def chat():
    """ 聊天列表管理 """
    chat_handler = ChatHandler()
    return jsonify(chat_handler.result)


@bp.route('/chat_message', methods=['GET', 'POST'])
def chat_message():
    chat_message_handler = ChatMessageHandler()
    return jsonify(chat_message_handler.result)


@bp.route('/upload_logo', methods=['POST'])
def upload_logo():
    """   上传头像  """
    # 获取图片
    print('upload..................')
    file= request.files.get('file')
    print('file..',file)
    content_type = file.content_type
    if content_type != 'image/jpeg':
        return jsonify(params_error(message='文件类型不正确'))
    # 生成图片名称
    image_name = str(uuid.uuid1()) + '.' + file.filename.split('.')[-1]
    image_path = '/static/logo/%s' % image_name
    try:
        with open('app' + image_path, 'wb') as f:
            f.write(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(server_error(message='上传失败'))

    ci = CutImage('app' + image_path, 'app' + image_path)
    ci.cut()

    return jsonify(success(data={'url': image_path}))
