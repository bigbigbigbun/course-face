from flask import Flask
from .views.views_student import stu
from .views.views_teacher import tch
from .views.views_admin import admin
from .views.views_leader import leader
from .views.attend_scheduler import *
from .exts import init_exts


def create_app():
    app = Flask(__name__)

    # 注册蓝图
    app.register_blueprint(blueprint=stu)
    app.register_blueprint(blueprint=tch)
    app.register_blueprint(blueprint=admin)
    app.register_blueprint(blueprint=leader)

    # 配置数据库
    db_uri = 'mysql+pymysql://root:123456@localhost:3306/face'  # mysql的配置
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化插件
    init_exts(app=app)
    scheduler.start()
    return app



