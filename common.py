# -*- coding:utf-8 -*-
import configparser
import logging
import time

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
