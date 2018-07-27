# -*- coding:utf-8 -*-
import os
import sys
import configparser
import time

__authro__ = 'Bill'


def get_file_dir():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"


exe_path = get_file_dir()
configPath = get_file_dir() + 'server.ini'
listenServiceSectionName = "ListenService"
listenOptionName = "listenServices"
servSuffix = ".py"


def get_config():
    config = configparser.ConfigParser()
    config.read(configPath)
    return config


def get_ai_service(exe_path):
    fileList = os.listdir(exe_path)
    list = []
    for file in fileList:
        if file.startswith("AI") and file.endswith(servSuffix):
            list.append(file)
    list.reverse()
    return list


def write_into_ini(ServersList):
    config = get_config()
    if len(ServersList):
        if not config.has_section(listenServiceSectionName): config.add_section(listenServiceSectionName)
        listenNames = ','.join(ServersList)
        config.set(listenServiceSectionName, listenOptionName, listenNames)
        with open(configPath, 'w+') as fc:
            config.write(fc)


def delete_ini_section():
    config = get_config()
    if config.has_section(listenServiceSectionName):
        if config.has_option(listenServiceSectionName, listenOptionName):
            config.remove_option(listenServiceSectionName, listenOptionName)
        config.remove_section(listenServiceSectionName)
    with open(configPath, 'w+') as fc:
        config.write(fc)


def get_process_count(imagename):
    p = os.popen('tasklist')
    return p.read().count(imagename)


class PhpEnv(object):
    apacheServd = ''
    apacheServdName = ''
    mysqlServd = ''
    mysqlServdName = ''
    installTask = []
    startTask = []
    stopTask = []
    removeTask = []
    START_ACTION = 'start'
    INSTALL_ACTION = 'install'
    UNINSTALL_ACTION = 'uninstall'
    REMOVE_ACTION = 'remove'
    STOP_ACTION = 'stop'

    def __init__(self):
        self.__iniServDconfig()

    def __iniServDconfig(self):
        config = get_config()
        self.mysqlServdName = config.get("PhpEnvListen", "mysqldName")
        self.mysqlServd = config.get("PhpEnvListen", "mysqlServd")
        self.apacheServdName = config.get("PhpEnvListen", "apacheName")
        self.apacheServd = config.get("PhpEnvListen", "apacheServd")

    def __iniStartTask(self):
        self.installTask.append(self.__getMysqldCmd(self.INSTALL_ACTION))
        self.installTask.append(self.__getApacheCmd(self.INSTALL_ACTION))
        self.startTask.append(self.__getMysqldCmd(self.START_ACTION))
        self.startTask.append(self.__getApacheCmd(self.START_ACTION))

    def __iniStopTask(self):
        self.stopTask.append(self.__getMysqldCmd(self.STOP_ACTION))
        self.stopTask.append(self.__getApacheCmd(self.STOP_ACTION))
        self.removeTask.append(self.__getMysqldCmd(self.REMOVE_ACTION))
        self.removeTask.append(self.__getApacheCmd(self.REMOVE_ACTION))

    def installAndStartServ(self):
        self.__iniStartTask()
        if len(self.installTask):
            for cmd in self.installTask:
                os.system(cmd)
        if len(self.startTask):
            for cmd in self.startTask:
                os.system(cmd)

    def uninstallServ(self):
        self.__iniStopTask()
        if len(self.stopTask):
            for cmd in self.stopTask:
                os.system(cmd)
        if len(self.removeTask):
            for cmd in self.removeTask:
                os.system(cmd)

    def __getMysqldCmd(self, action):
        __cmd = ''
        if action == self.INSTALL_ACTION:
            __cmd = self.mysqlServd + ' -' + self.INSTALL_ACTION + ' ' + self.mysqlServdName
        if action == self.START_ACTION:
            __cmd = 'net ' + self.START_ACTION + ' ' + self.mysqlServdName
        if action == self.STOP_ACTION:
            __cmd = 'net ' + self.STOP_ACTION + ' ' + self.mysqlServdName
        if action == self.REMOVE_ACTION:
            __cmd = self.mysqlServd + ' -' + self.REMOVE_ACTION + ' ' + self.mysqlServdName
        return __cmd

    def __getApacheCmd(self, action):
        __cmd = ''
        if action == self.INSTALL_ACTION:
            __cmd = self.apacheServd + ' -n ' + self.apacheServdName + ' -k ' + self.INSTALL_ACTION
        if action == self.START_ACTION:
            __cmd = self.apacheServd + ' -n ' + self.apacheServdName + ' -k ' + self.START_ACTION
        if action == self.STOP_ACTION:
            __cmd = self.apacheServd + ' -n ' + self.apacheServdName + ' -k ' + self.STOP_ACTION
        if action == self.REMOVE_ACTION:
            __cmd = self.apacheServd + ' -n ' + self.apacheServdName + ' -k ' + self.UNINSTALL_ACTION
        return __cmd


def doInstall():
    exe_path = get_file_dir()
    list = get_ai_service(exe_path)
    list.reverse()
    currAction = 'install'
    serviceNameList = []
    exe_path = get_file_dir()
    phpEnv = PhpEnv()
    print('Install PHPEnv...')
    phpEnv.installAndStartServ()
    time.sleep(4)
    print('Install Serve...')
    for service in list:
        if 'AIZYingListen' not in service:
            cmd = "python " + exe_path + service + " " + currAction
        else:
            cmd = "python " + exe_path + service + " --startup auto " + currAction
        os.system(cmd)
        serviceNameList.append(service[:-3])
    time.sleep(2)
    currAction = 'start'
    for service in list:
        cmd = "python " + exe_path + service + " " + currAction
        os.system(cmd)
    write_into_ini(serviceNameList)


def doUninstall():
    exe_path = get_file_dir()

    list = get_ai_service(exe_path)
    if len(list):
        currAction1 = 'stop'
        for service in list:
            cmd = "python " + exe_path + service + " " + currAction1
            os.system(cmd)
        print('Stopping Service...')
        serviceExecProcess = 'pythonservice.exe'
        time.sleep(2)
        if get_process_count(serviceExecProcess):
            cmd = 'taskkill /f /im ' + serviceExecProcess
            os.system(cmd)
            time.sleep(2)
        phantomjsProcess = 'phantomjs.exe'
        if get_process_count(phantomjsProcess):
            cmd = 'taskkill /f /im ' + phantomjsProcess
            os.system(cmd)
            time.sleep(2)
        print('Stop Succ! ...')
        time.sleep(2)
        print("Then remove services...")
        currAction2 = 'remove'
        for service in list:
            cmd = "python " + exe_path + service + " " + currAction2
            os.system(cmd)
        delete_ini_section()
        print('Remove PHPEnv...')
        time.sleep(4)
        phpEnv = PhpEnv()
        phpEnv.uninstallServ()
        print('Succ remove All Services!...')


INSTALL_CMD = 'install'
UNINSTALL_CMD = 'uninstall'


def main(args):
    cmd = args[1]
    if cmd == INSTALL_CMD:
        doInstall()
    if cmd == UNINSTALL_CMD:
        doUninstall()


if __name__ == '__main__':
    main(sys.argv)
