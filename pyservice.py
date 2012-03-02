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

class aservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonServiceExample"
    _svc_display_name_ = "Python Service - Just loops every second."
    _svc_deps_ = ["EventLog"]

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop=win32event.CreateEvent(None, 0, 0, None)
        self.isAlive=True
        
    def log(self, msg): 
		servicemanager.LogInfoMsg(str(msg))
        
    def SvcStop(self):
        # tell Service Manager we are trying to stop (required)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # set the event to call
        win32event.SetEvent(self.hWaitStop)

        self.isAlive=False

    def SvcDoRun(self):
        # Write a 'started' event to the event log... (not required)
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STARTED,0,servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))

        # methode 2: wait for beeing stopped ...
        self.timeout=1000  # In milliseconds (update every second)
		
        while self.isAlive:
            # win32api.Sleep(1*1000, True)
			
            # wait for service stop signal, if timeout, loop again
            rc=win32event.WaitForSingleObject(self.hWaitStop, self.timeout)

            print "looping %s " % sys.executable
            self.log("Looping")
            
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        return

if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        try:
            if "python.exe" in sys.executable:
                win32serviceutil.StartService(aservice._svc_name_)
            else:   
                servicemanager.Initialize('aservice', None)
                servicemanager.PrepareToHostSingle(aservice)
                servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            print "except - %s" % details
        # pass
    else:
        win32serviceutil.HandleCommandLine(aservice)