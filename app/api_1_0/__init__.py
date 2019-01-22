from flask import Blueprint

# 创建蓝图对象
bp = Blueprint('api_1_0', __name__)

# 导入蓝图的视图
from . import views