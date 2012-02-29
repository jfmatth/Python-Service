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
import time
import sys

class Service(win32serviceutil.ServiceFramework):
	_svc_name_ = None 
	_svc_display_name_ = None
	
	def __init__(self, *args):
		win32serviceutil.ServiceFramework.__init__(self, *args)
		self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def log(self, msg):
		servicemanager.LogInfoMsg(str(msg))
        
    def sleep(self, sec):
        win32api.Sleep(sec*1000, True)
        
	def SvcDoRun(self):
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		try:
			self.ReportServiceStatus(win32service.SERVICE_RUNNING)
			self.log('Starting %s' % self._svc_display_name_)
			self.start()
			win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
			self.log('%s Finished' % self._svc_display_name_)
		except Exception, x:
			self.log('Exception : %s' % x)
			self.SvcStop()

    def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.log('Service %s stopping ' % self._svc_display_name_)
		self.stop()
		self.log('%s ' % self._svc_display_name_)
		win32event.SetEvent(self.stop_event)
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
	
    def start(self):
        pass

    def stop(self):
        pass


class PythonService(Service):
    _svc_name_ = "aservice"
    _svc_display_name_ = "Sample Python service"
    _svc_deps_ = ["EventLog"]

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop=win32event.CreateEvent(None, 0, 0, None)
        self.isAlive=True

    def SvcStop(self):

        # tell Service Manager we are trying to stop (required)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # write a message in the SM (optional)
        # import servicemanager
        # servicemanager.LogInfoMsg("aservice - Recieved stop signal")

        # set the event to call
        win32event.SetEvent(self.hWaitStop)

        self.isAlive=False

    def SvcDoRun(self):
        import servicemanager
        # Write a 'started' event to the event log... (not required)
        #win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STARTED,0, servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))

        # methode 1: wait for beeing stopped ...
        # win32event.WaitForSingleObject(self.hWaitStop,win32event.INFINITE)

        # methode 2: wait for beeing stopped ...
        self.timeout=1000  # In milliseconds (update every second)

        while self.isAlive:

            # wait for service stop signal, if timeout, loop again
            rc=win32event.WaitForSingleObject(self.hWaitStop,self.timeout)

            print "looping"

        # and write a 'stopped' event to the event log (not required)
        #win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STOPPED,0, servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

	return

if __name__ == '__main__':

    # if called without argvs, let's run !

    
    # THIS IS THE MAGIC FOR PYINSTALLER.  Since we are running as "THE EXE", the main code has to connect and start the service, just
    # like pythonservice.exe does from PyWin32.
    if len(sys.argv) == 1:
        try:
	    #evtsrc_dll = os.path.abspath(servicemanager.__file__)
	    servicemanager.PrepareToHostSingle(aservice)
	    servicemanager.Initialize('aservice', None)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(aservice)