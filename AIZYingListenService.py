import datetime
import shutil
import winerror
import servicemanager
import win32event
import win32service
import configparser
import os
import sys
import psutil
import win32serviceutil
import time
from collections import OrderedDict

UNKNOWN = 0

STOPPED = 1

START_PENDING = 2

STOP_PENDING = 3

RUNNING = 4

status_code = {
    0: "UNKNOWN",
    1: "STOPPED",
    2: "START_PENDING",
    3: "STOP_PENDING",
    4: "RUNNING"
}


def is_iterable(source):
    if source is not None:
        try:
            iter(source)
        except TypeError:
            return False
        return True
    else:
        raise RuntimeError("argument cannot be None")


def status_service(service_name):
    try:
        result = win32serviceutil.QueryServiceStatus(service_name)[1]
        if result == START_PENDING:
            print("service %s is %s, please wait" % (service_name, status_code[result]))
            time.sleep(2)
            return RUNNING
        elif result == STOP_PENDING:
            print("service %s is %s, please wait" % (service_name, status_code[result]))
            time.sleep(2)
            return STOPPED
        else:
            return result if result is not None else 0
    except Exception as e:
        if e:
            raise RuntimeError(str(e))
        elif e.args:
            # print e.args
            args = list()
            for arg in e.args:
                if is_iterable(arg):
                    args.append(unicode(eval(repr(arg)), 'gbk'))
                else:
                    args.append(arg)
            print("Error:", args[-1], tuple(args))
            raise RuntimeError
        else:
            raise RuntimeError("Uncaught exception, maybe it is a 'Access Denied'")  # will not reach here


def start_service(service_name):
    status = status_service(service_name)
    if status == STOPPED:
        pass
    elif status == RUNNING:
        print("service %s already started" % service_name)
        return status
    try:
        print("starting %s" % service_name)
        win32serviceutil.StartService(service_name)
    except Exception as e:
        if e:
            raise RuntimeError(str(e))
        elif e.args:
            # print e.args
            args = list()
            for arg in e.args:
                if is_iterable(arg):
                    args.append(unicode(eval(repr(arg)), 'gbk'))
                else:
                    args.append(arg)
            print("Error:", args[-1], tuple(args))
            raise RuntimeError
        else:
            raise RuntimeError("Uncaught exception, maybe it is a 'Access Denied'")  # will not reach here

    return status_service(service_name)


def stop_service(service_name):
    status = status_service(service_name)
    if status == STOPPED:
        print("service %s already stopped" % service_name)
        return status
    elif status == RUNNING:
        pass
    else:
        return status
    try:
        print("stopping %s" % service_name)
        win32serviceutil.StopService(service_name)
    except Exception as e:
        if e:
            print(str(e))
        elif e.args:
            # print e.args
            args = list()
            for arg in e.args:
                if is_iterable(arg):
                    args.append(unicode(eval(repr(arg)), 'gbk'))
                else:
                    args.append(arg)
            print("Error:", args[-1], tuple(args))
            raise RuntimeError
        else:
            raise RuntimeError("Uncaught exception, maybe it is a 'Access Denied'")  # will not reach here

    return status_service(service_name)


def restart_service(service_name):
    status = status_service(service_name)
    if status == START_PENDING or status == RUNNING:
        if status == START_PENDING:
            time.sleep(2)
        stop_service(service_name)
        status = status_service(service_name)
        if status == STOPPED or status == STOP_PENDING:
            if status == STOP_PENDING:
                time.sleep(2)
            return start_service(service_name)
    elif status == STOPPED or status == STOP_PENDING:
        print("service %s not running." % service_name)
        return start_service(service_name)
    else:
        return status_service(service_name)


def do_service(service_name, service_action):
    valid_action = ["start", "stop", "restart", "status"]

    maps = {
        "start": "start_service(service_name)",
        "stop": "stop_service(service_name)",
        "restart": "restart_service(service_name)",
        "status": "status_service(service_name)",
    }

    if service_name == "" or service_action == "":
        raise RuntimeError("service_name and service_action cannot be empty.")

    if service_action in valid_action:
        return eval(maps[service_action])
    else:
        raise RuntimeError("bad service_action '%s', valid action is %s" % (service_action, valid_action))


def list_service():
    service_dict = OrderedDict()
    for service in psutil.win_service_iter():
        service_dict[service.name()] = service.display_name()
    return service_dict


def is_valid_service_name(service_name):
    if service_name.lower() in [name.lower() for name, display_name in list_service().items()]:
        return True
    else:
        return False


def get_file_dir():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"


def get_config_ini():
    configPath = get_file_dir() + 'server.ini'
    config = configparser.ConfigParser()
    config.read(configPath)
    return config


exe_path = get_file_dir()
config_file_path = exe_path + 'server.ini'
log_base = exe_path + 'logs\\'
log_path = log_base + 'winLog.log'


def out_put_filelog(taskInfo, fileName='winLog', tag='[info] : '):
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


class ServListenTask(object):
    __stopService = []

    def servListen(self):
        config = get_config_ini()
        listenServiceSectionName = "ListenService"
        listenOptionName = "listenServices"
        listener = str(config.get(listenServiceSectionName, listenOptionName)).split(',')

        stopService = []
        for listen in listener:
            code = do_service(listen, 'status')
            if code == STOPPED:
                msg = "Stop Server is : " + listen
                out_put_filelog(msg)
                stopService.append(listen)
            self.__stopService = stopService

    def hasStopServs(self):
        if len(self.__stopService) == 0:
            return False
        return True

    def servReStart(self):
        for listen in self.__stopService:
            do_service(listen, 'start')
            msg = "Restart Server is : " + listen
            out_put_filelog(msg)
        self.__stopService = []


class PhpEnvListenTask(object):
    apacheServd = ''
    apacheServdName = ''
    mysqlServd = ''
    mysqlServdName = ''
    taskMaps = {}
    startTask = []
    START_ACTION = 'start'

    def __init__(self):
        self.__iniServDconfig()

    def __iniServDconfig(self):
        config = get_config_ini()
        self.mysqlServdName = config.get("PhpEnvListen", "mysqldName")
        self.mysqlServd = config.get("PhpEnvListen", "mysqlServd")
        self.apacheServdName = config.get("PhpEnvListen", "apacheName")
        self.apacheServd = config.get("PhpEnvListen", "apacheServd")
        self.taskMaps[self.mysqlServdName] = self.__getMysqldCmd(self.START_ACTION)
        self.taskMaps[self.apacheServdName] = self.__getApacheCmd(self.START_ACTION)

    def __getMysqldCmd(self, action):
        __cmd = ''
        if action == self.START_ACTION:
            __cmd = 'net start ' + self.mysqlServdName
        return __cmd

    def __getApacheCmd(self, action):
        __cmd = ''
        if action == self.START_ACTION:
            __cmd = self.apacheServd + ' -n ' + self.apacheServdName + ' -k start'
        return __cmd

    def listenServ(self):
        if len(self.taskMaps):
            servKeys = list_service().keys()
            for task in list(self.taskMaps):
                currServName = task
                print(currServName)
                startCmd = self.taskMaps[currServName]
                if currServName not in servKeys:
                    print(currServName)
                    continue
                code = do_service(currServName, 'status')
                if code == STOPPED:
                    msg = "Stop PHPEnvServer is : " + currServName
                    out_put_filelog(msg)
                    self.startTask.append(startCmd)

    def servReStart(self):
        for cmd in self.startTask:
            msg = "Restart PHPEnvServer cmd : " + cmd
            out_put_filelog(msg)
            os.system(cmd)
        self.startTask = []

    def hasStopServs(self):
        if len(self.startTask) == 0:
            return False
        return True


class AIZYingListenService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AIZYingListenService"
    _svc_display_name_ = "AIID AIZYingListenService"
    _svc_description_ = "智影医疗AI服务监听组件"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.__listenTask = ServListenTask()
        self.__phpEnvTask = PhpEnvListenTask()

    def SvcDoRun(self):
        self.__run = True
        time.sleep(90)
        while self.__run:
            self.__phpEnvTask.listenServ()
            if self.__phpEnvTask.hasStopServs():
                time.sleep(4)
                self.__phpEnvTask.servReStart()
            time.sleep(4)

            self.__listenTask.servListen()
            if self.__listenTask.hasStopServs():
                time.sleep(4)
                self.__listenTask.servReStart()
            time.sleep(4)

    def SvcStop(self):
        self.__run = False
        time.sleep(2)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(AIZYingListenService)
            servicemanager.Initialize('AIZYingListenService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        import pickle

        modName = pickle.whichmodule(AIZYingListenService, AIZYingListenService.__name__)
        win32serviceutil.HandleCommandLine(AIZYingListenService)
