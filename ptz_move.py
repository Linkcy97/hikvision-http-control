import requests
from requests.auth import HTTPDigestAuth
import time

# 摄像头ip地址 用户名 密码
ip = '10.168.1.166'
admin = 'admin'
password = 'actl9239'

def preset_point(point):
    """预设点位"""
    session = requests.Session()
    url = 'http://%s/ISAPI/PTZCtrl/channels/1/presets/%d/goto' % (ip, point)
    session.put(url, auth=HTTPDigestAuth(admin, password))


def pan_tilt_move(pan_speed=0, tilt_speed=0, second=1):
    """控制摄像头旋转
    :param pan_speed:水平旋转:大于0右转,小于0左转
    :param tilt_speed:垂直旋转:大于0上升，小于0下降
    :param second:旋转的持续时间
    """
    session = requests.Session()
    url = 'http://%s/ISAPI/PTZCtrl/channels/1/continuous/' % ip
    param = "<PTZData><pan>%s</pan><tilt>%s</tilt></PTZData>" % (pan_speed, tilt_speed)
    param1 = "<PTZData><pan>0</pan><tilt>0</tilt></PTZData>"
    session.put(url, data=param, auth=HTTPDigestAuth(admin, password))
    time.sleep(second)
    session.put(url, data=param1, auth=HTTPDigestAuth(admin, password))


def change_wdr(mode='close', level=0):
    """设置宽动态等级
    :param mode:宽动态打开还是关闭 open or close
    :param level:宽动态等级 0-100
    """
    session = requests.Session()
    url = 'http://%s/ISAPI/Image/channels/1/WDR' % ip
    param = "<WDR><mode>%s</mode><WDRLevel>%d</WDRLevel></WDR>" % (mode, level)
    session.put(url, data=param, auth=HTTPDigestAuth(admin, password))


def change_color(brightness=50, contrast=50, saturation=50):
    """
    改变摄像头拍照参数
    :param brightness: 亮度 0-100
    :param contrast: 对比度 0-100
    :param saturation: 锐度 0-100
    :return:
    """
    session = requests.Session()
    url = 'http://%s/ISAPI/Image/channels/1/color' % ip
    param = "<Color>" \
            "<brightnessLevel>%d</brightnessLevel>" \
            "<contrastLevel>%d</contrastLevel>" \
            "<saturationLevel>%d</saturationLevel>" \
            "</Color>" % (brightness, contrast, saturation)
    session.put(url, data=param, auth=HTTPDigestAuth(admin, password))


def change_hlc(enabled='false'):
    """
    摄像头强光抑制
    :param enabled:开启true 关闭false
    :return:
    """
    session = requests.Session()
    url = 'http://%s/ISAPI/Image/channels/1/HLC' % ip
    param = '<HLC><enabled>%s</enabled></HLC>' % enabled
    session.put(url, data=param, auth=HTTPDigestAuth(admin, password))


def change_scenario(mode='custom1'):
    """
    设置摄像头场景
    :param mode:场景模式 可选值：indoor outdoor day night morning nightfall street lowIllumination custom1 custom2
    :return:
    """
    session = requests.Session()
    url = 'http://%s/ISAPI/Image/channels/1/mountingScenario' % ip
    param = '<MountingScenario><mode>%s</mode></MountingScenario>' % mode
    session.put(url, data=param, auth=HTTPDigestAuth(admin, password))


def change_zoom(zoom,second=1.0):
    """
    摄像头变焦
    :param zoom:倍数 大于0放大 小于0缩小
    :param second:持续时间
    :return:
    """
    session = requests.Session()
    url = 'http://%s/ISAPI/PTZCtrl/channels/1/continuous' % ip
    param = '<PTZData><zoom>%d</zoom></PTZData>' % zoom
    param1 = '<PTZData><zoom>0</zoom></PTZData>'
    session.put(url, data=param, auth=HTTPDigestAuth(admin, password))
    time.sleep(second)
    session.put(url, data=param1, auth=HTTPDigestAuth(admin, password))

if __name__ == '__main__':
    pass
