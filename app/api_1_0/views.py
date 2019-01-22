from . import bp
from flask import request, jsonify, current_app, session
from app import redis_store, db
from app.models import User
from sqlalchemy.exc import IntegrityError

@bp.route('/user', methods=['POST'])
def register():
    """
    用户注册
    请求参数： 用户名， 密码
    :return:
    """