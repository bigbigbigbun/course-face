from ..exts import db


class ClassModel(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    students = db.relationship('StudentModel', backref='class', lazy=True)


StudentCourseModel = db.Table(
    'students_courses',
    db.Column('s_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('c_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)


# AttendanceModel = db.Table(
#     'attendances',
#     db.Column('id', db.Integer, primary_key=True, autoincrement=True),
#     db.Column('time', db.Time),
#     db.Column('result', db.String(30)),
#     db.Column('s_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
#     db.Column('c_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
# )


# class AttendModel:
#     pass


class AttendanceModel(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.Time)
    result = db.Column(db.String(30))
    s_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    c_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)


class StudentModel(db.Model):
    # 表名
    __tablename__ = 'students'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    sex = db.Column(db.Boolean, default=True)
    pwd = db.Column(db.String(30))

    class_id = db.Column(db.Integer, db.ForeignKey(ClassModel.id))

    faces = db.relationship('FaceModel', backref='students', lazy=True)


class TeacherModel(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    sex = db.Column(db.Boolean, default=True)
    pwd = db.Column(db.String(80))
    classes = db.Column(db.String(80))

    courses = db.relationship('CourseModel', backref='teachers', lazy=True)


class CourseModel(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    week = db.Column(db.Integer)
    time = db.Column(db.Time)
    address = db.Column(db.String(30))

    t_id = db.Column(db.Integer, db.ForeignKey(TeacherModel.id), nullable=False)

    stu_course = db.relationship('StudentModel', backref='stu_course', secondary=StudentCourseModel, lazy='dynamic')
    stu_attend = db.relationship('StudentModel', backref='stu_attend', secondary=AttendanceModel.__tablename__,
                                 lazy='dynamic')


class FaceModel(db.Model):
    __tablename__ = 'face'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    face_img = db.Column(db.String(80))
    face_info = db.Column(db.String(80))
    result = db.Column(db.String(30))

    s_id = db.Column(db.Integer, db.ForeignKey(StudentModel.id))
