from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()


def init_exts(app):
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    scheduler.init_app(app)
