# -*- coding: utf-8 -*-   
# Author       : Li Chongyang of ACTL 
# Email        : lichongyang2016@163.com
# Date         : 2021-07-16 16:28:49
# LastEditors  : Li Chongyang of ACTL
# LastEditTime : 2022-10-18 14:57:05
# FilePath     : \PythonProject\Xiamen_pi\camera.py

import requests
from requests.auth import HTTPDigestAuth
import time, datetime
import traceback
import logging
import multiprocessing
import cv2
import os

logging.basicConfig(filename='log/camera_log.txt',
                    level=logging.ERROR,
                    format='[%(asctime)s] [%(levelname)s] >>> \n%(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')


def print_log(func):
    """
    装饰器，记录程序bug
    :param func:
    :return:
    """

    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            traceback.print_exc()
            logging.error(traceback.format_exc())

    return inner


class Camera(object):

    def __init__(self, ip, admin, password):
        """
        :param self.ip:摄像头self.ip地址
        :param self.admin: 用户名
        :param self.password: 密码
        """
        self.ip = ip
        self.admin = admin
        self.password = password

    def img_catch(self, return_dict, img_name):
        return_dict['img_name'] = None
        date_img = str(datetime.date.today())
        if not os.path.isdir('./img/%s' % date_img):
            os.makedirs('./img/%s' % date_img)

        ptz_capture = cv2.VideoCapture("rtsp://%s:%s@%s:554//h264/ch1/main" % (self.admin, self.password, self.ip))
        success, img = ptz_capture.read()

        if img_name == '':
            return_dict['img_name'] = str(datetime.datetime.today())[:-7].replace(':', ';') + '.jpg'
        else:
            return_dict['img_name'] = img_name
        if success:
            cv2.imwrite('./img/%s/%s' % (date_img, return_dict['img_name']), img)
            print('Image Catched! Image named:', return_dict['img_name'])

    def catch(self, img_name=''):
        """
        摄像头拍照函数
        :param img_name:拍摄照片命名
        :return: 拍摄照片名
        """

        #  通过manager保存子进程的参数
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        for _ in range(0, 3):
            p = multiprocessing.Process(target=self.img_catch, args=(return_dict, img_name))
            # 开启线程
            p.start()
            # 中断程序时间 4s
            p.join(4)
            if p.is_alive():
                p.terminate()
                p.join()
            if return_dict['img_name'] is not None:
                return return_dict['img_name']

        logging.error("Failed to capture three times\n")
        return return_dict['img_name']

    @print_log
    def preset_point(self, point):
        """预设点位"""
        session = requests.Session()
        url = 'http://%s/ISAPI/PTZCtrl/channels/1/presets/%d/goto' % (self.ip, point)
        session.put(url, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def pan_tilt_move(self, pan_speed=0, tilt_speed=0, second=1.0):
        """控制摄像头旋转
        :param pan_speed:水平旋转:大于0右转,小于0左转
        :param tilt_speed:垂直旋转:大于0上升，小于0下降
        :param second:旋转的持续时间
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/PTZCtrl/channels/1/continuous/' % self.ip
        param = "<PTZData><pan>%s</pan><tilt>%s</tilt></PTZData>" % (pan_speed, tilt_speed)
        param1 = "<PTZData><pan>0</pan><tilt>0</tilt></PTZData>"
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))
        time.sleep(second)
        session.put(url, data=param1, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_wdr(self, mode='close', level=0):
        """设置宽动态等级
        :param mode:宽动态打开还是关闭 open or close
        :param level:宽动态等级 0-100
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/Image/channels/1/WDR' % self.ip
        param = "<WDR><mode>%s</mode><WDRLevel>%d</WDRLevel></WDR>" % (mode, level)
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_color(self, brightness=50, contrast=50, saturation=50):
        """
        改变摄像头拍照参数
        :param brightness: 亮度 0-100
        :param contrast: 对比度 0-100
        :param saturation: 锐度 0-100
        :return:
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/Image/channels/1/color' % self.ip
        param = "<Color>" \
                "<brightnessLevel>%d</brightnessLevel>" \
                "<contrastLevel>%d</contrastLevel>" \
                "<saturationLevel>%d</saturationLevel>" \
                "</Color>" % (brightness, contrast, saturation)
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))
        print('change_color OK')

    @print_log
    def change_sharpness(self, level=50):
        """
        调整图像锐度
        :param level: 0-100
        :return:
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/Image/channels/1/sharpness' % self.ip
        param = "<Sharpness><SharpnessLevel>71</SharpnessLevel></Sharpness>" % level
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_hlc(self, enabled='false'):
        """
        摄像头强光抑制
        :param enabled:开启true 关闭false
        :return:
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/Image/channels/1/HLC' % self.ip
        param = '<HLC><enabled>%s</enabled></HLC>' % enabled
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_scenario(self, mode='custom1'):
        """
        设置摄像头场景
        :param mode:场景模式 可选值：indoor outdoor day night morning nightfall street lowIllumination custom1 custom2
        :return:
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/Image/channels/1/mountingScenario' % self.ip
        param = '<MountingScenario><mode>%s</mode></MountingScenario>' % mode
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_zoom(self, zoom, second=1.0):
        """
        摄像头变焦
        :param zoom:倍数 大于0放大 小于0缩小
        :param second:持续时间
        :return:
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/PTZCtrl/channels/1/continuous' % self.ip
        param = '<PTZData><zoom>%d</zoom></PTZData>' % zoom
        param1 = '<PTZData><zoom>0</zoom></PTZData>'
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))
        time.sleep(second)
        session.put(url, data=param1, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_day_night(self, mode='day'):
        """
        摄像头变焦
        :param mode:day or night
        :return:
        """
        session = requests.Session()
        url = 'http://%s/ISAPI/Image/channels/1/ircutFilter' % self.ip
        param = '<IrcutFilter><IrcutFilterType>%s</IrcutFilterType><nightToDayFilterLevel>4</nightToDayFilterLevel></IrcutFilter>' % mode
        session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

    @print_log
    def change_exposure(self, level=50, model='auto', shutter_lever='1/100'):
        """
        改变曝光
        :param shutter_lever: 快门
        :param model: 曝光模式
        :param level: 曝光增益
        :return:
        """
        session = requests.Session()
        exposuer_url = 'http://%s/ISAPI/Image/channels/1/exposure' % self.ip
        shutter_url = 'http://%s/ISAPI/Image/channels/1/shutter' % self.ip
        if model == 'auto':
            param = '<Exposure><ExposureType>auto</ExposureType>' \
                    '<OverexposeSuppress><enabled>false</enabled></OverexposeSuppress></Exposure>'
            session.put(exposuer_url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

            # 增益限制
            url = 'http://%s/ISAPI/Image/channels/1/gain' % self.ip
            param = '<Gain><GainLimit>%d</GainLimit></Gain>' % level
            session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

            # 最大快门限制  最小快门限制
            param = '<Shutter><ShutterLevel>1/100</ShutterLevel>' \
                    '<maxShutterLevelLimit>1/50</maxShutterLevelLimit>' \
                    '<minShutterLevelLimit>1/10000</minShutterLevelLimit></Shutter>'
            session.put(shutter_url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

        if model == 'manual':
            param = '<Exposure><ExposureType>manual</ExposureType>' \
                    '<OverexposeSuppress><enabled>false</enabled></OverexposeSuppress></Exposure>'
            session.put(exposuer_url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

            url = 'http://%s/ISAPI/Image/channels/1/gain' % self.ip
            param = '<Gain><GainLevel>%d</GainLevel></Gain>' % level
            session.put(url, data=param, auth=HTTPDigestAuth(self.admin, self.password))

            param = '<Shutter><ShutterLevel>%s</ShutterLevel></Shutter>' % shutter_lever
            session.put(shutter_url, data=param, auth=HTTPDigestAuth(self.admin, self.password))


if __name__ == '__main__':
    C1 = Camera('10.168.1.166', 'admin', 'actl9239')
    C1.camera_catch()
