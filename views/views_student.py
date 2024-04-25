from io import BytesIO

from flask import Blueprint, render_template, request, redirect, jsonify
from sqlalchemy import not_, and_

from ..models.models import *
from functools import wraps
from .face import *


stu = Blueprint('stu', __name__)


# 装饰器：登录验证
def login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        # 判断用户是否登录了
        # 获取cookie，得到登录的用户
        s_id = request.cookies.get('s_id', None)
        if s_id:
            # 登录过，进入后台管理系统
            user = StudentModel.query.get(s_id)
            request.user = user
            return fn(*args, **kwargs)
        else:
            # 如果没有登录，则跳转到登录页面
            return redirect('/login/')

    return inner


# 学生登录
@stu.route('/')
@stu.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('home/student/login.html')

    elif request.method == "POST":
        userid = request.form.get('userid')  # 用户名
        password = request.form.get('password')  # 密码

        # 登录验证，验证用户名和密码是否匹配
        user = StudentModel.query.filter_by(id=userid, pwd=password).first()
        if user:
            # 登录成功
            response = redirect('/index/')
            response.set_cookie('s_id', str(user.id), max_age=7 * 24 * 3600)

            return response
        else:
            return redirect('/login/')


# 学生首页
@stu.route('/index/', methods=['GET', 'POST'])
@login_required
def stu_index():
    user = request.user
    face = FaceModel.query.filter_by(s_id=user.id).first()

    return render_template('home/student/index.html',
                           username=user.name,
                           face=face
                           )


# 登出
@stu.route('/logout/')
def stu_logout():
    response = redirect('/login/')
    response.delete_cookie('user_id')
    return response


# 学生个人信息
@stu.route('/stu_info/', methods=['GET', 'POST'])
@login_required
def stu_info():
    user = request.user
    my_face = FaceModel.query.filter_by(s_id=user.id).count()
    if my_face == 0:
        path_face = os.path.join('App/static/face/', user.name)
        print(path_face)
        os.makedirs(path_face, exist_ok=True)
        s_face = FaceModel()
        s_face.face_img = path_face
        s_face.result = '否'
        s_face.s_id = user.id
        try:
            db.session.add(s_face)
            db.session.commit()
            print('ok')
        except Exception as e:
            print('e', e)
            db.session.rollback()

    return render_template('home/student/stu_info.html',
                           user=user
                           )


# 修改密码
@stu.route('/stu_pwd/', methods=['GET', 'POST'])
@login_required
def stu_pwd():
    if request.method == "POST":
        print('111')
        user = request.user
        oldPwd = request.form.get('oldPassword')
        newPwd = request.form.get('newPassword')

        if oldPwd != newPwd:
            if oldPwd == user.pwd:
                student = StudentModel.query.get(user.id)
                student.id = user.id
                student.pwd = newPwd
                try:
                    db.session.commit()
                except Exception as e:
                    print('e', e)
                return redirect('/stu_info/')
            else:
                return redirect('/stu_info/')
        else:
            return redirect('/stu_info/')


# 学生选课页面
@stu.route('/select_course/', methods=['GET', 'POST'])
@login_required
def select_course():
    user = request.user
    courses = CourseModel.query.all()   # 获取所有课程
    # 获取选课表中用户所选的所有课程的c_id
    sc = db.session.query(StudentCourseModel.c.c_id).filter(StudentCourseModel.c.s_id == user.id).subquery()
    # 在课程表中筛选出不在已选课程中的数据
    filtered_course = CourseModel.query.filter(not_(CourseModel.id.in_(sc))).all()

    return render_template('home/student/select_course.html',
                           courses=filtered_course
                           )


# 学生选课
@stu.route('/add_select_course/', methods=['GET', 'POST'])
@login_required
def add_select_course():

    if request.method == 'POST':
        user_id = request.user.id
        c_id = request.form.get('id')

        # 添加选课记录
        user = StudentModel.query.filter_by(id=user_id).first()
        course = CourseModel.query.filter_by(id=c_id).first()

        try:
            user.stu_course.append(course)
            db.session.commit()
        except Exception as e:
            print('e', e)
            db.session.rollback()
        return jsonify({'code': 200, 'msg': '选课成功'})
    else:
        return jsonify({'code': 400, 'msg': '选课失败'})


# 学生退课
@stu.route('/del_select_course/', methods=['GET', 'POST'])
@login_required
def del_select_course():
    if request.method == 'GET':
        user = request.user
        user_course = db.session.query(StudentCourseModel.c.c_id).filter(StudentCourseModel.c.s_id == user.id).subquery()
        filtered_course = CourseModel.query.filter(CourseModel.id.in_(user_course)).all()

        return render_template('home/student/del_select_course.html',
                               courses=filtered_course
                               )

    if request.method == 'POST':
        user_id = request.user.id
        c_id = request.form.get('id')

        # 删除所选课程
        course = and_(StudentCourseModel.c.s_id == user_id, StudentCourseModel.c.c_id == c_id)

        try:
            db.session.query(StudentCourseModel).filter(course).delete()
            db.session.commit()
        except Exception as e:
            print('e', e)
            db.session.rollback()
        return jsonify({'code': 200, 'msg': '退课成功'})
    else:
        return jsonify({'code': 400, 'msg': '退课失败'})


# 考勤查询
@stu.route('/attend/', methods=['GET', 'POST'])
@login_required
def attend():
    user = request.user
    attends = AttendanceModel.query.filter_by(s_id=user.id).all()
    for attend in attends:
        course = CourseModel.query.get(attend.c_id)
        attend.course = course.name

    return render_template('home/student/attend.html',
                            attends=attends
                           )


# 人脸录入
@stu.route('/face/', methods=['GET', 'POST'])
@login_required
def face():
    if request.method == 'GET':
        # user = request.user

        return render_template('home/student/face.html')

    elif request.method == 'POST':
        user = request.user
        # 获取前端上传的图片
        file = request.files['image']
        # 读取图片内容存到 BytesIO 对象中
        image_io = BytesIO(file.read())
        # 将 BytesIO 对象解码为 OpenCV 图像
        img = cv2.imdecode(np.asarray(bytearray(image_io.read()), dtype=np.uint8), cv2.IMREAD_COLOR)

        my_face_all = FaceModel.query.filter_by(s_id=user.id).first()

        face_vectors, file_face_model = add_face_info(img, user.name, my_face_all.face_img)
        if len(face_vectors) > 0:
            s_face = FaceModel.query.filter_by(s_id=user.id).first()
            s_face.result = '是'
            s_face.face_info = file_face_model
        try:
            db.session.commit()
        except Exception as e:
            print('e', e)
        return jsonify({'code': 200, 'msg': '人脸录入成功'})
    else:
        return jsonify({'code': 400, 'msg': '人脸录入成功'})


# 学生签到
@stu.route('/stu_sign_in/', methods=['GET', 'POST'])
@login_required
def stu_sign_in():
    user = request.user
    if request.method == 'GET':
        user_course = db.session.query(StudentCourseModel.c.c_id).filter(
            StudentCourseModel.c.s_id == user.id).subquery()
        filtered_course = CourseModel.query.filter(CourseModel.id.in_(user_course)).all()
        return render_template('home/student/sign_in.html',
                               courses=filtered_course
                               )
    elif request.method == 'POST':
        # 获取前端上传的图片和课程id
        file = request.files['image']
        c_id = request.form.get('c_id')
        # 读取图片内容存到 BytesIO 对象中diz
        image_io = BytesIO(file.read())
        # 将 BytesIO 对象解码为 OpenCV 图像
        img = cv2.imdecode(np.asarray(bytearray(image_io.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
        my_face_all = FaceModel.query.filter_by(s_id=user.id).first()
        face_models = [np.load(my_face_all.face_info)]
        detector = dlib.get_frontal_face_detector()  # dlib人脸检测器
        sp = dlib.shape_predictor("App/static/face/shape_predictor_68_face_landmarks_GTX.dat")  # 人脸标志检测器
        # 人脸特征提取器
        facerec = dlib.face_recognition_model_v1("App/static/face/dlib_face_recognition_resnet_model_v1.dat")
        while True:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换格式
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度
            face_rects = detector(gray, 0)  # 检测人脸
            for k, rect in enumerate(face_rects):  # 遍历检测的人脸
                cv2.rectangle(img, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 0, 255), 2)
                shape = sp(img_rgb, rect)  # 标志点检测
                face_vector = facerec.compute_face_descriptor(img_rgb, shape)  # 获取人脸特征

                # 计算人脸特征和人脸模型的距离
                face_name, score = face_recognize(np.array(face_vector), face_models, user.name)  # 进行识别，返回id和距离
                if score < 0.35:  # 设定阈值来判定是否为同一人
                    attendance = AttendanceModel()
                    attendance.s_id = user.id
                    attendance.c_id = c_id
                    attendance.time = datetime.datetime.now()
                    attendance.result = '是'
                    try:
                        db.session.add(attendance)
                        db.session.commit()
                    except Exception as e:
                        print('e', e)
                        db.session.rollback()
                    return jsonify({'code': 200, 'msg': '签到成功'})
                else:
                    return jsonify({'code': 400, 'msg': '签到失败'})
    else:
        return jsonify({'code': 400, 'msg': '请求方式错误'})
