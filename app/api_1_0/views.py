from flask import request, jsonify, current_app, session, render_template, redirect, url_for
from . import bp
from app import redis_store, socketio
from .login import LoginHandler, LogoutHandler
from .chat import ChatHandler
from .user import UserHandler, UserInfoHandler
from .group import GroupHandler, QuitGroupHandler
from .group_user import GroupUserHandler
from .friend import FriendHandler, FriendInfoHandler
from .chat_message import ChatMessageHandler
from utils.restful import server_error, params_error, success, unauth_error
from utils.cut_image import CutImage
from .libs.send_message import SendMessage
from app.models import *

import uuid


@socketio.on('message')
def handle_json(request_data):
    SendMessage(request_data)


@socketio.on('in_chat')
def in_chat():
    """
    用户进入聊天页面，将用户的id和sid绑定，为chat_sid_userid = sid
    :return:
    """
    print('---------------用户进入聊天页面---------------')
    print(session.get('nickname'), session.get('id'), request.sid)
    print('---------------end---------------')
    if not chat:
        return
    sid = request.sid
    user_id = session.get('id')
    sid_key = 'chat_sid_%s' % user_id
    redis_store.set(sid_key, sid, 3600*12)


@socketio.on('out_chat')
def out_chat():
    """
    用户退出聊天界面，删除用户的sid
    :return:
    """
    print('-----------------用户退出聊天页面----------------')
    print(session.get('nickname'), session.get('id'), request.sid)
    print('-----------------end-------------------')
    user_id = session.get('id')
    sid_key = 'chat_sid_%s' % user_id
    redis_store.delete(sid_key)


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
    if session.get('id'):
        return render_template('index.html')

    login_url = url_for('.login', _external=True)
    return redirect(login_url)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    用户名、 密码
    :return:
    """
    index_url = url_for('.index', _external=True)
    login_handler = LoginHandler(index_url)

    if session.get('id'):
        return redirect(index_url)

    if request.method == 'GET':
        return login_handler.get_()

    return login_handler.post_()


@bp.route('/check_login', methods=['GET'])
def check_login():
    """
    检查用户是否登录
    :return:
    """
    user_id = session.get('id')
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
    logout_handler = LogoutHandler()
    return jsonify(logout_handler.result)


@bp.route('/group', methods=['GET', 'POST', 'PUT', 'DELETE'])
def group():
    """  群组管理 """
    group_handler = GroupHandler()
    return jsonify(group_handler.result)


@bp.route('/quit_group', methods=['DELETE'])
def quit_group():
    """ 退出群组 """
    quit_group_handler = QuitGroupHandler()
    return jsonify(quit_group_handler.result)


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


@bp.route('/friend_info', methods=['GET'])
def friend_info():
    """
    获取好友信息
    """
    friend_info_handler = FriendInfoHandler()
    return jsonify(friend_info_handler.result)


@bp.route('/chat', methods=['GET', 'POST', 'DELETE'])
def chat():
    """ 聊天列表管理 """
    chat_handler = ChatHandler()
    return jsonify(chat_handler.result)


@bp.route('/chat_message', methods=['GET', 'POST'])
def chat_message():
    chat_message_handler = ChatMessageHandler()
    return jsonify(chat_message_handler.result)


@bp.route('/upload_image', methods=['POST'])
def upload_image():
    """   上传图片  """
    # 获取图片
    print('upload..................')
    file= request.files.get('file')
    print('file..',file)
    content_type = file.content_type
    if content_type != 'image/jpeg':
        return jsonify(params_error(message='文件类型不正确'))
    # 生成图片名称
    image_name = str(uuid.uuid1()) + '.' + file.filename.split('.')[-1]
    image_path = '/static/images/%s' % image_name
    try:
        with open('app' + image_path, 'wb') as f:
            f.write(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(server_error(message='上传失败'))

    # ci = CutImage('app' + image_path, 'app' + image_path)
    # ci.cut()

    return jsonify(success(data={'url': image_path}))


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


@bp.route('/get_html', methods=['GET'])
def get_html():
    """  获取html源码 """
    import requests
    html = 'http://www.baidu.com'
    resp = requests.get(html)
    text = resp.text
    resp.close()
    return jsonify(success(data=text))