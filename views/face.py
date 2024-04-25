import sys
import cv2
import os
import numpy as np
import uuid  # 生成随机文件名
import dlib
from PIL import Image, ImageDraw, ImageFont
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel


def getMax_faces(face_rects):
    if len(face_rects) == 0:
        return 0, 0
    face_areas = []
    for rect in face_rects:
        # 计算每个人脸的面积（高x宽）只录入最大的那个人脸
        area = (rect.bottom() - rect.top()) * (rect.right() - rect.left())
        face_areas.append(area)
    index = np.argmax(face_areas)
    return face_areas[index], face_rects[index]


def gen_face_name(str_face_name):
    # 生成图片文件
    return str_face_name + '_' + str(uuid.uuid4()) + '.jpg'


def add_face_info(img, username, face_img):
    det_face = dlib.get_frontal_face_detector()  # 创建人脸检测器
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度
    face_rects = det_face(gray, 0)  # 检测人脸区域
    max_area, max_rect = getMax_faces(face_rects)  # 得到最大的人脸
    if max_area > 10:  # 保存最大人脸
        roi = img[max_rect.top(): max_rect.bottom(), max_rect.left(): max_rect.right()]
        # 生成文件名
        save_face_name = os.path.join('App/static/face', username, gen_face_name(username))
        cv2.imencode('.jpg', roi)[1].tofile(save_face_name)  # 保存
        print('save_face', save_face_name)

    # 加载人脸特征提取器
    facerec = dlib.face_recognition_model_v1("App/static/face/dlib_face_recognition_resnet_model_v1.dat")
    # 加载人脸标志点检测器
    sp = dlib.shape_predictor("App/static/face/shape_predictor_68_face_landmarks_GTX.dat")
    # 记录所有模型信息
    face_dir = face_img

    if os.path.isdir(face_dir):
        file_face_model = os.path.join(face_dir, username + '.npy')  # 遍历username文件夹
        face_vectors = []  # 人脸特征list

    for face_img in os.listdir(face_dir):  # 遍历，查找所有文件
        if os.path.splitext(face_img)[-1] == '.jpg':  # 寻找所有.jpg文件
            # 解码图像
            img = cv2.imdecode(np.fromfile(os.path.join(face_dir, face_img), dtype=np.uint8), -1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = np.array(img)  # 存放的是已经截取好的人脸图片，所以在图内检测标志点
            h, w, _ = np.shape(img)
            rect = dlib.rectangle(0, 0, w, h)  # 整个区域
            shape = sp(img, rect)  # 辅助人脸定位，获取关键位
            print("Generate face vector of", face_img)
            face_vector = facerec.compute_face_descriptor(img, shape)  # 获取128维人脸特征
            face_vectors.append(face_vector)  # 保存图像和人脸id
            # name(face_id)
    if len(face_vectors) > 0:  # 人脸模型保存
        np.save(file_face_model, face_vectors)
    #     print('save faceinfo success')
    return face_vectors, file_face_model


def face_recognize(face_vec, face_models, face_name):  # 计算欧氏距离，越相似数值越小
    scores = []
    for model in face_models:
        N = model.shape[0]
        diffMat = np.tile(face_vec, (N, 1))-model
        # 计算欧式距离
        sqDiffMat = diffMat ** 2
        sqDistances = sqDiffMat.sum(axis=1)
        distances = sqDistances ** 0.5
        # 找到最小距离
        score = np.min(distances)
        scores.append(score)
    index = np.argmin(scores)
    return face_name[index], scores[index]  # 返回name和距离