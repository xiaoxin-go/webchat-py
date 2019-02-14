from . import bp
from flask import request, jsonify, current_app, session, render_template
from app import redis_store, db
from app.models import User, Group, GroupsToUser
from sqlalchemy.exc import IntegrityError
from .methods import UserHandler, GroupHandler, GroupUserHandler


@bp.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    """  用户管理  """
    user_handler = UserHandler()
    return jsonify(user_handler.result)


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
    user_id = session.get('id')

    # 返回已登录状态，和用户数据
    return jsonify({'state': 1, 'user_data': {'username': username, 'nickname': nickname, 'id': user_id}})


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


@bp.route('/group', methods=['GET', 'POST', 'PUT', 'DELETE'])
def group():
    """  群组管理 """
    group_handler = GroupHandler()
    return jsonify(group_handler.result)


@bp.route('/group_add', methods=['GET','POST', 'PUT', 'DELETE'])
def group_user():
    """  群组成员管理 """
    group_user_handler = GroupUserHandler()
    return jsonify(group_user_handler.result)



