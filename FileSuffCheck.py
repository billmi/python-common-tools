# -*- coding:utf-8 -*-
import os

__authro__ = 'Bill'



'''
    用于文件后缀解析判断
    @author:Bill
    @Date: 2018/07/16
'''


class FileSuffCheck(object):

    @staticmethod
    def file_sufis_png(file):
        suffix = os.path.splitext(file)[1].lower()
        if suffix == '.png':
            return True
        return False

    @staticmethod
    def file_sufis_ini(file):
        suffix = os.path.splitext(file)[1].lower()
        if suffix == '.ini':
            return True
        return False

    @staticmethod
    def file_sufis_dcm(file):
        suffix = os.path.splitext(file)[1].lower()
        if suffix == '.dcm':
            return True
        return False
