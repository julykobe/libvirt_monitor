import libvirt
import sys

conn=libvirt.openReadOnly(None)
if conn==None:
	print "fail"
	sys.exit(1)
else:
	print "success"

