from ..exts import db


class AdminUserModel(db.Model):
    # 表名
    __tablename__ = 'admin'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True)
    passwd = db.Column(db.String(30))
