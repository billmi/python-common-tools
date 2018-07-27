import gc
import shutil
import win32process
import psutil
import win32serviceutil
import win32service
import win32event
import winerror
import servicemanager
import os, sys, time, datetime
import configparser
import pickle
import multiprocessing
from apscheduler.schedulers.blocking import BlockingScheduler
from abc import ABCMeta, abstractmethod
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

multiprocessing.freeze_support()


def get_file_dir():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"


exe_path = get_file_dir()
config_path = exe_path + "config.ini"
classFyExec = 'D:\\Anaconda3\\python.exe'
taskWorks = ["1", "2", "3", "4"]
log_base = exe_path + 'logs\\'
log_path = log_base + 'pilbt.log'


def get_config():
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


# write file
def out_put_filelog(taskInfo, fileName='log'):
    _maxFileSize = 1024 * 1024 * 500
    _logPath = log_path
    currAction = "a+"
    suffix = '.log'
    if len(fileName) > 0:
        _logPath = log_base + fileName + suffix
    if os.path.exists(_logPath):
        fileSize = os.path.getsize(_logPath)
        if fileSize >= _maxFileSize:
            bakLogDir = log_base + 'bak\\'
            if not os.path.exists(bakLogDir):
                os.mkdir(bakLogDir)
                time.sleep(1)
            _nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            _bankPath = bakLogDir + fileName + '_' + _nowTime + suffix
            shutil.copy(_logPath, _bankPath)
            currAction = 'w'
    with open(_logPath, currAction) as file:
        _nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = _nowTime + '--' + taskInfo + " -" + " \r\n"
        file.write(msg)
        file.close()


'''
    AIPILBTService : include func: ticker,classfy,parseDicom,png2Dicom,iniDataIn (main >> task lib)
    @author : Bill
'''


class AIPILBTService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AIPILBTService"
    _svc_display_name_ = "AIID AIPILBTService"
    _svc_description_ = "ZyingAI程序PILBT服务组件"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.__work = WorkerScheduler()

    def SvcDoRun(self):
        self.__run = True
        self.__work.run()
        while self.__run:
            time.sleep(2)

    def SvcStop(self):
        self.__run = False
        self.__work.stop()
        time.sleep(4)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


'''
    @name : Base
    @author : Bill
'''


class Abs(multiprocessing.Process):
    __metaclass__ = ABCMeta

    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.__run = True

    @abstractmethod
    def run(self): pass

    def stop(self):
        self._stop(self.pid)

    def _stop(self, p):
        self.__run = False
        if psutil.pid_exists(p):
            os.kill(p, 9)


'''
    @name : TaskPLBS
    @author : Bill
    @include : classfy,parseDicom,png2Dicom,iniDataIn,ticker
'''


class TaskPLBS(Abs):
    __lib = "task.py"
    _limitNum = 20
    _Neo = "4"

    def __init__(self, cmd):
        super(TaskPLBS, self).__init__()
        self.cuCmd = cmd
        self.__run = True

    def workc(self):
        scanDir = self.workPlan()
        list = os.listdir(scanDir)
        if len(list):
            time.sleep(1)
            k = 0
            if self.cuCmd == self._Neo: self.SetL()
            for i in range(0, len(list)):
                path = os.path.join(scanDir, list[i])
                if os.path.isfile(path):
                    args = ' ' + exe_path + self.__lib + ' ' + self.cuCmd + ' '
                    argv = args + path
                    if self.cuCmd != self._Neo:
                        time.sleep(2)
                        self.oCmd(classFyExec + argv)
                    else:
                        self.pCmd(classFyExec, argv)
                k += 1
                if k == self._limitNum: break
            time.sleep(1)

    def SetL(self):
        self._limitNum = 3

    def oCmd(self, Exec):
        os.system(Exec)

    def pCmd(self, Exec, argv):
        win32process.CreateProcess(Exec, argv, None, None, 0, win32process.CREATE_NO_WINDOW, None, None,
                                   win32process.STARTUPINFO())

    def workPlan(self):
        config = get_config()
        scanDir = ""
        if self.cuCmd == "1":
            scanDir = config.get("png2Dicom", "newpngdir")
        if self.cuCmd == "2":
            scanDir = config.get("parseDICOM", "parseinput")
        if self.cuCmd == "3":
            scanDir = config.get("ini2Database", 'inidir')
        if self.cuCmd == "4":
            scanDir = config.get("classfyAndLocationPng", "png1024path")
        return scanDir

    def run(self):
        while self.__run:
            self.workc()
            gc.collect()
            time.sleep(2)


'''
   Class : BAT CMD Collection
   @author : Bill
'''


class BatWork(object):

    @classmethod
    def DoPhpDcmWorker(self):
        batDir = exe_path + "bat\\"
        batFile = 'dcm.bat'
        BatWork.OutCmd(batDir + batFile)

    @classmethod
    def DoPhpIniWorker(self):
        batDir = exe_path + "bat\\"
        batFile = 'ini.bat'
        BatWork.OutCmd(batDir + batFile)

    @classmethod
    def OutCmd(self, Exec):
        win32process.CreateProcess(Exec, '', None, None, 0, win32process.CREATE_NO_WINDOW, None, None,
                                   win32process.STARTUPINFO())

    @classmethod
    def DoVMWorker(self):
        batDir = exe_path + "bat\\"
        batFile = 'startVmware.bat'
        os.system(batDir + batFile)


'''
   Class : Bat Ticker
   @author : Bill
'''


class Ticker(Abs):

    def __init__(self):
        super(Ticker, self).__init__()
        self.__blockingScheduler = BlockingScheduler()

    def __addTask(self):
        self.__blockingScheduler.add_job(BatWork.DoPhpDcmWorker, IntervalTrigger(seconds=6))
        self.__blockingScheduler.add_job(BatWork.DoPhpIniWorker, IntervalTrigger(seconds=6))
        self.__blockingScheduler.add_job(BatWork.DoVMWorker, DateTrigger(
            (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')))

    def run(self):
        self.__addTask()
        try:
            self.__blockingScheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.__blockingScheduler.shutdown()

    def stop(self):
        self.__blockingScheduler.shutdown()


'''
    All work Scheduler Implement
    @author : Bill
'''


class WorkerScheduler(object):
    worker = []
    cmdStart = "start"
    cmdStop = "stop"

    def __init__(self):
        self.__iniWorkers()

    def __iniWorkers(self):
        for work in taskWorks:
            self.worker.append(TaskPLBS(work))
        self.worker.append(Ticker())

    def DoWork(self, cmd):
        for work in self.worker:
            if cmd == self.cmdStart:
                work.start()
            if cmd == self.cmdStop:
                work.stop()

    def run(self):
        self.DoWork(self.cmdStart)

    def stop(self):
        self.DoWork(self.cmdStop)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(AIPILBTService)
            servicemanager.Initialize('AIPILBTService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        modName = pickle.whichmodule(AIPILBTService, AIPILBTService.__name__)
        win32serviceutil.HandleCommandLine(AIPILBTService)
