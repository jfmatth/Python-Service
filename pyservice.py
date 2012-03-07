# Usage:
# service.exe install
# service.exe start
# service.exe stop
# service.exe remove

# you can see output of this program running python site-packages\win32\lib\win32traceutil

import win32service
import win32serviceutil
import win32event
import win32evtlogutil
import win32traceutil
import servicemanager
import winerror
import win32api
import time
import sys
import os

# allows us to try each of the service "wait" techniques.
sWait = True

class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonServiceExample"
    _svc_display_name_ = "Python Service - Just loops every second."
    _svc_deps_ = ["EventLog"]

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True

    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))

    def SvcStop(self):
        # tell Service Manager we are trying to stop (required)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # set the event to call
        win32event.SetEvent(self.hWaitStop)

        self.isAlive = False

    def SvcDoRun(self):
        # Write a 'started' event to the event log... (not required)
        win32evtlogutil.ReportEvent(self._svc_name_,
                                    servicemanager.PYS_SERVICE_STARTED,
                                    0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                                    (self._svc_name_, '')
                                    )

        self.log("Started %s" % self._svc_name_)

        # print some environment and change things if necessary.
        print "sys.executable = %s" % sys.executable
        print "__file__ = %s" % __file__
        print "curdir %s " % os.getcwd()
        print "dirname of __file__ %s" % os.path.dirname(__file__)
        print "Changig directory to %s" % os.path.dirname(__file__)
        os.chdir(os.path.dirname(__file__))
        print "curdir %s " % os.getcwd()

        # two ways of running a service:
        #   1. Just wait for it to receive a stop command
        #   2. Loop and wait for the command, with a timeout in each wait.
        if sWait:
            # method 1
            win32event.WaitForSingleObject(self.hWaitStop,win32event.INFINITE)
        else:
            # methode 2: wait for being stopped ...
            self.timeout = 10000  # In milliseconds (10 seconds)

            while self.isAlive:
                # win32api.Sleep(1*1000, True)

                # wait for service stop signal, if timeout, loop again
                rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
                self.log("Looping")

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        return

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PythonService)