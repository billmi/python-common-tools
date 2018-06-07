# -*- coding:utf-8 -*-
import configparser
import logging
import os
import sys
import time
import pydicom
import pymysql
from skimage import exposure, img_as_float
import matplotlib.pyplot as plt

from selenium import webdriver

__authro__ = 'Bill'

import datetime

'''
    用于直接写日志
    Demo : 
        获取后调用
        logger.info(u'任务开始....')
'''


def out_put_filelog(taskInfo, fileName='log'):
    file = fileName + '.txt'
    with open(file, 'a+') as file:
        _nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = "taskLog: " + _nowTime + '--' + taskInfo + '--' + " \r\n"
        file.write(msg)
        file.close()


'''
    用于log日志独占初始化
    Demo:
        获取对象后
        config.get("ini2Database", "iniDir")
'''


def get_log(logName):
    logger = logging.getLogger('save')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logName + '.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


'''
    config解析对象获取
    Demo : 
        [sec]
        index=123
        arg1 : 选择器  arg2 : 索引
        config.get("sec", "index")
'''


def get_config(config_file_path):
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config


'''
    用于模拟无头浏览器截屏,注意phantomjs下bin\phantomjs.exe需要加入环境变量
'''


def screen_web(httpUrl, savePath):
    brower = webdriver.PhantomJS()
    brower.get(httpUrl)
    time.sleep(8)
    brower.save_screenshot(savePath)
    print(u"---------图片已保存 : " + savePath + "-----------")
    brower.close()

'''
    mysql连接,连接池直接使用组件
    标识结果集:
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
'''

def get_mysql_conn(host='127.0.0.1', port=3306, user='root', passwd='root', db='test',charset='utf8'):
    return pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)


'''
    返回程序执行目录
'''

def get_file_dir():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"


'''
    暂时存档,需要使用后提取    
'''

def dicom_2png(file):
    _currFile = file
    try:
        dcm = pydicom.dcmread(file)
        out_put_filelog("Dicom [error] : file : " + file, 'scanFile')
        fileName = os.path.basename(file)
        imageX = dcm.pixel_array
        temp = imageX.copy()
        print("shape ----", imageX.shape)
        picMax = imageX.max()
        vmin = imageX.min()
        vmax = temp[temp < picMax].max()
        # print("vmin : ", vmin)
        # print("vmax : ", vmax)
        imageX[imageX > vmax] = 0
        imageX[imageX < vmin] = 0
        # result = exposure.is_low_contrast(imageX)
        # # print(result)
        image = img_as_float(imageX)
        plt.cla()
        plt.figure('adjust_gamma', figsize=(10.24, 10.24))
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
        plt.imshow(image, 'gray')
        plt.axis('off')
        plt.savefig(fileName + '.png')
        time.sleep(1)
    except Exception as e:
        info = sys.exc_info()
        out_put_filelog(
            "Dicom [error] : file : " + _currFile + "--- error:" + str(e) + "track : " + str(info[0]) + ":" + str(
                info[1]))
    finally:
        plt.close()
