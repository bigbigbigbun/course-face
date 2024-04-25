from functools import wraps
from flask import Blueprint, render_template, request, redirect
from sqlalchemy.orm import registry
from ..models.models import *
from ..models.models_leader import *

leader = Blueprint('leader', __name__)


# 装饰器：登录验证
def leader_login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        # 判断用户是否登录了
        # 获取cookie，得到登录的用户
        l_id = request.cookies.get('l_id', None)
        if l_id:
            # 登录过，进入后台管理系统
            user = LeaderModel.query.get(l_id)
            request.user = user
            return fn(*args, **kwargs)
        else:
            # 如果没有登录，则跳转到登录页面
            return redirect('/leader/login/')

    return inner


# 领导登录
@leader.route('/leader/')
@leader.route('/leader/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('leader/leader_login.html')

    elif request.method == "POST":
        userid = request.form.get('userid')  # 用户名
        password = request.form.get('password')  # 密码

        # 登录验证，验证用户名和密码是否匹配
        user = LeaderModel.query.filter_by(id=userid, passwd=password).first()
        if user:
            # 登录成功
            response = redirect('/leader/index/')
            response.set_cookie('l_id', str(user.id), max_age=7 * 24 * 3600)

            return response
        else:
            return redirect('/leader/login/')


# 退出
@leader.route('/leader/logout/')
def leader_logout():
    response = redirect('/leader/login/')
    response.delete_cookie('l_id')
    return response


# 领导首页
@leader.route('/leader/index/', methods=['GET', 'POST'])
@leader_login_required
def leader_index():
    user = request.user

    return render_template('leader/leader_index.html',
                           username=user.name
                           )


# 修改密码
@leader.route('/leader/leader_pwd/', methods=['GET', 'POST'])
@leader_login_required
def tch_pwd():
    if request.method == 'GET':
        return render_template('leader/update_leader_pwd.html')
    if request.method == 'POST':
        user = request.user
        oldPwd = request.form.get('oldPassword')
        newPwd = request.form.get('newPassword')

        if oldPwd != newPwd:
            if oldPwd == user.passwd:
                leader = LeaderModel.query.get(user.id)
                leader.id = user.id
                leader.passwd = newPwd
                try:
                    db.session.commit()
                except Exception as e:
                    print('e', e)
                return redirect('/leader/leader_pwd/')
            else:
                return redirect('/leader/leader_pwd/')
        else:
            return redirect('/leader/leader_pwd/')


# 教师信息
@leader.route('/leader/tch_info/', methods=['GET', 'POST'])
@leader_login_required
def tch_info():
    if request.method == 'GET':
        teachers = TeacherModel.query.all()

        for teacher in teachers:
            class_ids = teacher.classes

            for class_id in class_ids:
                class_id = int(class_id)
                classes = ClassModel.query.get(class_id)
                if classes:
                    teacher.courses_name = classes.name

        return render_template('leader/tch_info.html',
                               teachers=teachers
                               )


# 班级信息
@leader.route('/leader/class_info/', methods=['GET', 'POST'])
@leader_login_required
def class_info():
    if request.method == 'GET':
        classes = ClassModel.query.all()

        for class_info in classes:
                count = StudentModel.query.filter_by(class_id=class_info.id).count()
                class_info.stu_count = count

        return render_template('leader/class_info.html',
                               classes=classes
                               )


# 班级学生
@leader.route('/leader/class_student/<class_id>', methods=['GET', 'POST'])
@leader_login_required
def class_student(class_id):
    if request.method == 'GET':
        students = StudentModel.query.filter_by(class_id=class_id)

        return render_template('leader/class_student.html',
                               students=students
                               )


# 课程信息
@leader.route('/leader/course_info/', methods=['GET', 'POST'])
@leader_login_required
def course_info():
    if request.method == 'GET':
        courses = CourseModel.query.all()

        return render_template('leader/course_info.html',
                               courses=courses
                               )


# 课程考勤信息
@leader.route('/leader/attendance_info/<c_id>', methods=['GET', 'POST'])
@leader_login_required
def attendance_info(c_id):
    if request.method == 'GET':
        registry()
        # mapper(AttendModel, AttendanceModel)
        attendances = AttendanceModel.query.filter_by(c_id=c_id).all()
        print(attendances)
        for attendance in attendances:
                student = StudentModel.query.get(attendance.s_id)
                attendance.s_name = student.name

        return render_template('leader/attendance_info.html',
                               attendances=attendances
                               )


