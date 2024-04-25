from flask import Blueprint, render_template, request, redirect, jsonify
from functools import wraps
from ..models.models import *

tch = Blueprint('tch', __name__)


# 装饰器
def tch_login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        # 判断用户是否登录了
        # 获取cookie，得到登录的用户
        t_id = request.cookies.get('t_id', None)
        if t_id:
            # 登录过，进入后台管理系统
            user = TeacherModel.query.get(t_id)
            request.user = user
            return fn(*args, **kwargs)
        else:
            # 如果没有登录，则跳转到登录页面
            return redirect('/tch/login/')

    return inner


# 教师登录
@tch.route('/tch/')
@tch.route('/tch/login/', methods=['GET', 'POST'])
def tch_login():
    if request.method == 'GET':
        return render_template('home/teacher/tch_login.html')

    elif request.method == "POST":
        userid = request.form.get('userid')  # 用户名
        password = request.form.get('password')  # 密码

        # 登录验证，验证用户名和密码是否匹配
        user = TeacherModel.query.filter_by(id=userid, pwd=password).first()
        if user:
            # 登录成功
            response = redirect('/tch/index/')
            response.set_cookie('t_id', str(user.id), max_age=7 * 24 * 3600)

            return response
        else:
            return redirect('/tch/login/')


# 退出
@tch.route('/tch/logout/')
def tch_logout():
    response = redirect('/tch/login/')
    response.delete_cookie('t_id')
    return response


# 教师首页
@tch.route('/tch/index/', methods=['GET', 'POST'])
@tch_login_required
def tch_index():
    user = request.user

    return render_template('home/teacher/tch_index.html',
                           username=user.name
                           )


# 修改密码
@tch.route('/tch/tch_pwd/', methods=['GET', 'POST'])
@tch_login_required
def tch_pwd():
    if request.method == 'GET':
        return render_template('home/teacher/update_tch_pwd.html')
    if request.method == 'POST':
        user = request.user
        oldPwd = request.form.get('oldPassword')
        newPwd = request.form.get('newPassword')

        if oldPwd != newPwd:
            if oldPwd == user.pwd:
                teacher = TeacherModel.query.get(user.id)
                teacher.id = user.id
                teacher.pwd = newPwd
                try:
                    db.session.commit()
                except Exception as e:
                    print('e', e)
                return redirect('/tch/tch_pwd/')
            else:
                return redirect('/tch/tch_pwd/')
        else:
            return redirect('/tch/tch_pwd/')


# 我的课程
@tch.route('/tch/my_course/', methods=['GET', 'POST'])
@tch_login_required
def my_course():
    user = request.user
    courses = CourseModel.query.filter_by(t_id=user.id)

    return render_template('home/teacher/my_course.html',
                           courses=courses
                           )


# 我的学生
@tch.route('/tch/my_student/<cid>', methods=['GET', 'POST'])
@tch_login_required
def my_student(cid):
    user = request.user
    courses = CourseModel.query.get(cid)

    return render_template('home/teacher/my_student.html',
                           courses=courses
                           )


# 考勤记录
@tch.route('/tch/stu_attend/<cid>', methods=['GET', 'POST'])
@tch_login_required
def stu_attend(cid):
    # attends = db.session.query(AttendanceModel.c.id,
    #                            AttendanceModel.c.time,
    #                            AttendanceModel.c.result,
    #                            StudentModel.id.label('s_id'),
    #                            StudentModel.name.label('s_name')). \
    #     join(StudentModel, AttendanceModel.c.s_id == StudentModel.id). \
    #     filter(AttendanceModel.c.c_id == cid)

    attends = AttendanceModel.query.filter_by(c_id=cid).all()
    for attend in attends:
        student = StudentModel.query.get(attend.s_id)
        attend.student_name = student.name
    course = CourseModel.query.get(cid)

    return render_template('home/teacher/stu_attend.html',
                           attends=attends,
                           courses=course
                           )


# @tch.route('/tch/no_attend/<cid>', methods=['GET', 'POST'])
# @tch_login_required
# def no_attend(cid):
#     attends = AttendanceModel.query.filter_by(c_id=cid).all()
#     course = CourseModel.query.get(cid)
#     for attend in attends:
#         if attend.s_id != course.stu_course.id:
