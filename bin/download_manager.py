#!/usr/bin/python -u

import sys
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import tftpy
import Openbmc
if (len(sys.argv) < 2):
	print "Usage:  download_manager.py [system name]"
	exit(1)
System = __import__(sys.argv[1])


DBUS_NAME = 'org.openbmc.managers.Download'
OBJ_NAME = '/org/openbmc/managers/Download'
TFTP_PORT = 69

class DownloadManagerObject(dbus.service.Object):
	def __init__(self,bus,name):
		dbus.service.Object.__init__(self,bus,name)
		bus.add_signal_receiver(self.DownloadHandler, 
			dbus_interface = "org.openbmc.Flash", signal_name = "Download", path_keyword = "path")

	@dbus.service.signal(DBUS_NAME,signature='ss')
	def DownloadComplete(self,outfile,filename):
		print "Download Complete: "+outfile
		return outfile

	@dbus.service.signal(DBUS_NAME,signature='s')
	def DownloadError(self,filename):
		pass

	def DownloadHandler(self,url,filename,path = None):
		try:
			filename = str(filename)
			client = tftpy.TftpClient(url, TFTP_PORT)
			print "Downloading: "+filename+" from "+url
			outfile = System.FLASH_DOWNLOAD_PATH+"/"+filename
			client.download(filename,outfile)
			obj = bus.get_object("org.openbmc.control.Flash",path)
			intf = dbus.Interface(obj,"org.openbmc.Flash")
			intf.update(outfile)
					
		except Exception as e:
			print "ERROR DownloadManager: "+str(e)
			obj = bus.get_object("org.openbmc.control.Flash",path)
			intf = dbus.Interface(obj,"org.openbmc.Flash")
			intf.error("Download Error: "+filename)


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = Openbmc.getDBus()
    name = dbus.service.BusName(DBUS_NAME, bus)
    obj = DownloadManagerObject(bus, OBJ_NAME)
    mainloop = gobject.MainLoop()
    
    print "Running Download Manager"
    mainloop.run()

