from . import bp
from flask import request, jsonify, current_app, session, render_template
from app import redis_store, db
from app.models import User, Group, GroupsToUser
from sqlalchemy.exc import IntegrityError


@bp.route('/user', methods=['POST'])
def register():
    """
    用户注册
    请求参数： 用户名， 密码
    :return:
    """
    request_data = request.json

    username = request_data.get('username')
    password = request_data.get('password')
    nickname = request_data.get('nickname')

    # 检查用户名和密码是否存在
    if not all([username, password]):
        return jsonify({'state': 2, 'message': '缺少必要参数'})

    # 添加用户
    user_obj = User(username=username, nickname=nickname)

    # 设置密码
    user_obj.password = password        # 已自动加密

    try:
        db.session.add(user_obj)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚
        db.session.rollback()
        # 此错误信息表示用户被注册过
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '用户已存在'})
    except Exception as e:
        db.session.rollback()
        # 数据库操作异常
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '添加用户异常'})

    # 注册成功
    return jsonify({'state': 1, 'message': '注册成功'})


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    用户名、 密码
    :return:
    """

    # 获取用户传输数据
    request_data = request.json
    username = request_data.get('username')
    password = request_data.get('password')

    if not all([username, password]):
        return jsonify({'state': 2, 'message': '缺少必要参数'})

    # 获取用户登录IP
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums and int(access_nums) >= 5:
            return jsonify({'state': 2, 'message': '错误次数过多，请稍后重试'})

    # 从数据库查询用户对象
    try:
        user_obj = User.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '获取用户信息失败'})

    # 取出用户密码与数据库密码对比
    if not user_obj or not user_obj.check_password(password):
        # 如果用户不存在或者用户密码不正确，返回错误消息，并记录错误次数
        try:
            # redis的incr可以对字符串类型数据进行加1操作，如果数据开始不存在，则默认设置为1
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, 600)  # 数据保存600秒
        except Exception as e:
            current_app.logger.error(e)

        return jsonify({'state': 2, 'message': '用户名或密码错误'})

    # 登录成功
    session['username'] = username
    session['nickname'] = user_obj.nickname
    session['id'] = user_obj.id

    return jsonify({'state': 1, 'message': '登录成功'})


@bp.route('/check_login', methods=['GET'])
def check_login():
    """
    检查用户是否登录
    :return:
    """
    username = session.get('username')
    if not username:
        return jsonify({'state': 2, 'message': '用户未登录'})

    nickname = session.get('nickname')
    id = session.get('id')

    # 返回已登录状态，和用户数据
    return jsonify({'state': 1, 'user_data': {'username': username, 'nickname': nickname, 'id': id}})


@bp.route('/', methods=['GET'])
def index():
    """
    返回项目主页
    :return:
    """
    return render_template('index.html')


@bp.route('/logout', methods=['POST'])
def logout():
    """ 用户退出登录 """
    session.clear()     # 清除用户session
    return jsonify({'state': 1,'message': '用户退出成功'})


@bp.route('/user', methods=['PUT'])
def user():
    """  修改用户信息 """

    request_data = request.json
    username = request_data.get('username')
    if not username:
        return jsonify({'state': 2, 'message': '缺失必要参数'})
    old_password = request_data.get('old_password')

    try:
        user_obj = User.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '获取用户信息失败'})

    if not user_obj:
        return jsonify({'state': 2, 'message': '用户不存在'})

    # 如果密码存在，则为修改密码
    if old_password:
        new_password = request_data.get('new_password')
        if not new_password:
            return jsonify({'state': 2, 'message': '缺失必要参数'})

        # 原密码不正确
        if not user_obj.check_password(old_password):
            return jsonify({'state': 2, 'message': '原密码不正确'})

        # 检验成功，修改用户密码
        user_obj.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'state': 2, 'message': '修改密码异常'})

        return jsonify({'state': 1, 'message': '密码修改成功'})
    # 否则为修改昵称
    else:
        nickname = request_data.get('nickname')
        if not nickname:
            return jsonify({'state': 2, 'message': '缺失必要参数'})

        user_obj.nickname = nickname
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'state': 2, 'message': '修改昵称异常'})

        return jsonify({'state': 1, 'message': '昵称修改成功'})


@bp.route('/group', methods=['GET', 'POST', 'PUT', 'DELETE'])
def group():
    """ 新建群组 """


@bp.route('/group_add', methods=['POST'])
def group_extend():
    """  群组添加好友 """

    request_data = request.json

    # 获取群组ID
    group_id = request_data.get('group_id')
    if not group_id:
        return jsonify({'state': 2, 'message': '缺失必要参数'})

    # 获取添加的好友列表
    member_list = request_data.get('friend_list')
    if not member_list:
        return jsonify({'state': 2, 'message': '缺失必要参数'})

    # 判断群组是否存在
    try:
        group_obj = Group.query.get(group_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '群组信息查询异常'})

    if not group_obj:
        return jsonify({'state': 2, 'message': '群组不存在'})

    # 添加群组信息
    for user_id in member_list:
        # 判断添加的用户是否存在
        try:
            user_obj = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            continue
        # 不存在跳过
        if not user_obj:
            continue

        # 存在则添加到群组表中
        group_user_obj = GroupsToUser(group_id=group_id, user_id=user_id)
        db.session.add(group_user_obj)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify({'state': 2, 'message': '添加异常'})

    return jsonify({'state': 1, 'message': '添加成功'})



