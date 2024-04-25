from ..exts import db


class LeaderModel(db.Model):
    # 表名
    __tablename__ = 'leader'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True)
    passwd = db.Column(db.String(30))
