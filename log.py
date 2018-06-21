# -*- coding:utf-8 -*-
import datetime
import logging
import os
import shutil
import sys
import time

__authro__ = 'Bill'


def get_file_dir():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"


exe_path = get_file_dir()
config_file_path = exe_path + 'config.ini'
log_base = exe_path + 'logs\\'
log_path = log_base + 'taskLog.txt'

LOG_NAME = 'save_png_in.log'


# 用于一般日志
def out_put_filelog(taskInfo, fileName='log', tag='[info] : '):
    _maxFileSize = 1024 * 1024 * 500
    _logPath = log_path
    currAction = "a+"
    suffix = '.log'
    if len(fileName) > 0:
        _logPath = log_base + fileName + suffix
    if os.path.exists(_logPath):
        fileSize = os.path.getsize(_logPath)
        if fileSize >= _maxFileSize:
            print('max ...')
            bakLogDir = log_base + 'bak\\'
            if not os.path.exists(bakLogDir):
                os.mkdir(bakLogDir)
                time.sleep(1)
            _nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            _bankPath = bakLogDir + fileName + '_' + _nowTime + '.log'
            shutil.copy(_logPath, _bankPath)
            currAction = 'w'
    with open(_logPath, currAction) as file:
        _nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = _nowTime + ' task:' + fileName + ' ' + tag + '  ' + taskInfo + ' ' + " \r\n"
        file.write(msg)
        file.close()


# 用于错误日志
def out_err_filelog(taskInfo, fileName='errlog', tag='[error] : '):
    out_put_filelog(taskInfo, fileName, tag)


# def get_log(logName):
#     logger = logging.getLogger('save')
#     logger.setLevel(logging.DEBUG)
#     fh = logging.FileHandler(LOG_NAME)
#     fh.setLevel(logging.DEBUG)
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)
#     return logger

# i = 0
# while i <= 100:
#     out_put_filelog("4654564564564564545asdasdasdasdasdasdasdasdasd", 'cc', '[error] : ')
#     i += 1


def write_phantomjs_env():
    __curExeDir = os.path.dirname(os.path.abspath(__file__)) + "\\"
    phantomjs = 'phantomjs'
    jsBinPath = __curExeDir + phantomjs + '\\bin'
    if os.path.exists(jsBinPath):
        currEnv = os.environ['PATH']
        if phantomjs not in currEnv:
            os.environ['PATH'] = os.environ['PATH'] + ';' + jsBinPath + ';'


