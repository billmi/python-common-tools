# -*- coding:utf-8 -*-
import os

__authro__ = 'Bill'



'''
    用于文件后缀解析判断
    @author:Bill
    @Date: 2018/05/21
'''


class FileSuffCheck(object):

    @staticmethod
    def file_sufis_png(file):
        if os.path.splitext(file)[1].lower() == '.png':
            return True
        return False

    @staticmethod
    def file_sufis_ini(file):
        if os.path.splitext(file)[1].lower() == '.ini':
            return True
        return False

    @staticmethod
    def file_sufis_dcm(file):
        if os.path.splitext(file)[1].lower() == '.dcm' or os.path.splitext(file)[1] == '.DCM':
            return True
        return False
