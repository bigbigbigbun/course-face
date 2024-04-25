import os
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, jsonify
from ..models.models import *
from ..models.models_admin import *
from functools import wraps

from ..models.models_leader import LeaderModel

admin = Blueprint('admin', __name__)


# 装饰器
def admin_login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        # 判断用户是否登录了
        # 获取cookie，得到登录的用户
        admin_id = request.cookies.get('admin_id', None)
        if admin_id:
            # 登录过，进入后台管理系统
            user = AdminUserModel.query.get(admin_id)
            request.user = user
            return fn(*args, **kwargs)
        else:
            # 如果没有登录，则跳转到登录页面
            return redirect('/admin/login/')

    return inner


@admin.route('/admin/')
@admin.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')

    elif request.method == "POST":
        userid = request.form.get('userid')  # 用户名
        password = request.form.get('password')  # 密码

        # 登录验证，验证用户名和密码是否匹配
        user = AdminUserModel.query.filter_by(id=userid, passwd=password).first()
        if user:
            # 登录成功
            response = redirect('/admin/index/')
            response.set_cookie('admin_id', str(user.id), max_age=7 * 24 * 3600)

            return response
        else:
            return redirect('/admin/login/')


# 退出
@admin.route('/admin/logout/')
def admin_logout():
    response = redirect('/admin/login/')
    response.delete_cookie('admin_id')
    return response


# 管理员首页
@admin.route('/admin/index/', methods=['GET', 'POST'])
@admin_login_required
def admin_index():
    user = request.user

    return render_template('admin/admin_index.html',
                           username=user.name
                           )


# 修改密码
@admin.route('/admin/admin_pwd/', methods=['GET', 'POST'])
@admin_login_required
def tch_pwd():
    if request.method == 'GET':
        return render_template('admin/update_admin_pwd.html')
    if request.method == 'POST':
        user = request.user
        oldPwd = request.form.get('oldPassword')
        newPwd = request.form.get('newPassword')

        if oldPwd != newPwd:
            if oldPwd == user.passwd:
                admin = AdminUserModel.query.get(user.id)
                admin.id = user.id
                admin.passwd = newPwd
                try:
                    db.session.commit()
                except Exception as e:
                    print('e', e)
                return redirect('/admin/admin_pwd/')
            else:
                return redirect('/admin/admin_pwd/')
        else:
            return redirect('/admin/admin_pwd/')


# 添加学生
@admin.route('/admin/addstu/', methods=['GET', 'POST'])
@admin_login_required
def addstu():
    if request.method == 'GET':
        classes = ClassModel.query.all()
        students = StudentModel.query.all()
        for student in students:
            face = FaceModel.query.filter_by(s_id=student.id).first()
            if face:
                student.face_result = face.result
            else:
                student.face_result = '否'
        return render_template('admin/addstudent.html',
                               classes=classes,
                               students=students
                               )
    elif request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        sex = request.form.get('sex')
        pwd = request.form.get('pwd')
        class_id = request.form.get('class_id')

        student = StudentModel()
        if id:
            student.id = id
        student.name = name
        student.sex = bool(sex)
        student.pwd = pwd
        student.class_id = class_id

        try:
            db.session.add(student)
            db.session.commit()
        except Exception as e:
            print('e', e)
            db.session.rollback()
        return redirect('/admin/addstu/')
    else:
        return '请求方式错误'


# 修改学生信息
@admin.route('/admin/updatestu/<sid>', methods=['GET', 'POST'])
@admin_login_required
def updatestu(sid):
    student = StudentModel.query.get(sid)
    if request.method == 'GET':
        classes = ClassModel.query.all()
        return render_template('admin/updatestu.html',
                               student=student,
                               classes=classes
                               )
    if request.method == 'POST':
        name = request.form.get('name')
        sex = request.form.get('sex')
        pwd = request.form.get('pwd')
        class_id = request.form.get('class_id')
        student.name = name
        student.sex = bool(sex)
        student.pwd = pwd
        student.class_id = class_id
        try:
            db.session.commit()
        except Exception as e:
            print(e, 'e')
        return redirect('/admin/addstu/')


# 删除学生
@admin.route('/admin/delstu/<sid>', methods=['GET', 'POST'])
@admin_login_required
def delstu(sid):
    student = StudentModel.query.get(sid)
    try:
        db.session.delete(student)
        db.session.commit()
    except Exception as e:
        print('e:', e)
    return redirect('/admin/addstu/')


# 添加老师
@admin.route('/admin/addtch/', methods=['GET', 'POST'])
@admin_login_required
def addtch():
    if request.method == 'GET':
        classes = ClassModel.query.all()
        teachers = TeacherModel.query.all()
        for teacher in teachers:
            class1 = ClassModel.query.filter_by(id=teacher.classes).first()
            teacher.class_name = class1.name
        return render_template('admin/addteacher.html',
                               classes=classes,
                               teachers=teachers
                               )
    elif request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        sex = request.form.get('sex')
        pwd = request.form.get('pwd')
        class_id = request.form.get('class_id')

        teacher = TeacherModel()
        if id:
            teacher.id = id
        teacher.name = name
        teacher.sex = bool(sex)
        teacher.pwd = pwd
        teacher.classes = class_id

        try:
            db.session.add(teacher)
            db.session.commit()
        except Exception as e:
            print('e', e)
            db.session.rollback()
        return redirect('/admin/addtch/')
    else:
        return '请求方式错误'


# 修改教师信息
@admin.route('/admin/updatetch/<tid>', methods=['GET', 'POST'])
@admin_login_required
def updatetch(tid):
    teacher = TeacherModel.query.get(tid)
    if request.method == 'GET':
        classes = ClassModel.query.all()
        return render_template('admin/updatetch.html',
                               teacher=teacher,
                               classes=classes
                               )
    if request.method == 'POST':
        name = request.form.get('name')
        sex = request.form.get('sex')
        pwd = request.form.get('pwd')
        class_id = request.form.get('class_id')
        teacher.name = name
        teacher.sex = bool(sex)
        teacher.pwd = pwd
        teacher.classes = class_id
        try:
            db.session.commit()
        except Exception as e:
            print(e, 'e')
        return redirect('/admin/addtch/')


# # 删除教师
# @admin.route('/admin/deltch/<tid>', methods=['GET', 'POST'])
# @admin_login_required
# def deltch(tid):
#     teacher = TeacherModel.query.get(tid)
#     try:
#         db.session.delete(teacher)
#         db.session.commit()
#     except Exception as e:
#         print('e:', e)
#     return redirect('/admin/addtch/')


# 添加课程
@admin.route('/admin/addcourse/', methods=['GET', 'POST'])
@admin_login_required
def addcourse():
    if request.method == 'GET':
        teachers = TeacherModel.query.all()
        courses = CourseModel.query.all()
        return render_template('admin/addcourse.html',
                               teachers=teachers,
                               courses=courses
                               )
    elif request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        week = request.form.get('week')
        # time =
        time = datetime.strptime(request.form.get('time'), "%H:%M:%S")
        address = request.form.get('address')
        t_id = request.form.get('t_id')

        course = CourseModel()
        if id:
            course.id = id
        course.name = name
        course.week = week
        course.time = time
        course.address = address
        course.t_id = t_id

        try:
            db.session.add(course)
            db.session.commit()
        except Exception as e:
            print('e', e)
            db.session.rollback()
        return redirect('/admin/addcourse/')
    else:
        return '请求方式错误'


# 修改教师信息
@admin.route('/admin/updatecourse/<cid>', methods=['GET', 'POST'])
@admin_login_required
def updatecourse(cid):
    course = CourseModel.query.get(cid)
    if request.method == 'GET':
        teachers = TeacherModel.query.all()
        return render_template('admin/updatecourse.html',
                               teachers=teachers,
                               course=course
                               )
    if request.method == 'POST':
        name = request.form.get('name')
        week = request.form.get('week')
        time = request.form.get('time')
        address = request.form.get('address')
        t_id = request.form.get('t_id')
        course.name = name
        course.week = week
        course.time = time
        course.address = address
        course.t_id = t_id
        try:
            db.session.commit()
        except Exception as e:
            print(e, 'e')
        return redirect('/admin/addcourse/')


# 删除学生
@admin.route('/admin/delcourse/<cid>', methods=['GET', 'POST'])
@admin_login_required
def delcourse(cid):
    course = CourseModel.query.get(cid)
    try:
        db.session.delete(course)
        db.session.commit()
    except Exception as e:
        print('e:', e)
    return redirect('/admin/addcourse/')


# 添加领导
@admin.route('/admin/addleader/', methods=['GET', 'POST'])
@admin_login_required
def addleader():
    if request.method == 'GET':
        leaders = LeaderModel.query.all()
        return render_template('admin/addleader.html',
                               leaders=leaders
                               )
    elif request.method == 'POST':
        name = request.form.get('name')
        pwd = request.form.get('pwd')

        leader = LeaderModel()
        leader.name = name
        leader.passwd = pwd

        try:
            db.session.add(leader)
            db.session.commit()
        except Exception as e:
            print('e', e)
            db.session.rollback()
        return redirect('/admin/addleader/')
    else:
        return '请求方式错误'


# 删除学生人脸
@admin.route('/admin/delface/', methods=['GET', 'POST'])
@admin_login_required
def delface():
    if request.method == 'GET':
        faces = FaceModel.query.all()
        return render_template('admin/delface.html',
                               faces=faces
                               )

    elif request.method == 'POST':
        id = request.form.get('id')
        face = FaceModel.query.get(id)
        path_face = os.path.join(face.face_img)
        files = os.listdir(path_face)
        for f in files:
            os.remove(os.path.join(path_face, f))
        try:
            db.session.delete(face)
            db.session.commit()
        except Exception as e:
            print('e:', e)
        return jsonify({'code': 200, 'msg': '删除成功'})
    else:
        return jsonify({'code': 400, 'msg': '请求方式错误'})
