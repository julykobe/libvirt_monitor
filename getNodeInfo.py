import libvirt
import os,sys,re,time
from xml.etree import ElementTree

def get_devices(dom,path,devs):
	tree=ElementTree.fromstring(dom.XMLDesc(0))
	devices=[]
	for target in tree.findall(path):
		dev=target.get(devs)
		if not dev in devices:
			devices.append(dev)
	return devices

def get_blockStats(dom):
	block_status={}
	disks=get_devices(dom,"devices/disk/target","dev")
	for block in disks:
		block_status[block]=dom.blockStats(block)
	return block_status

def get_domDiskInfo(dom0):
	block_status0={}
	block_status1={}
	disk_info=''
	block_status0=get_blockStats(dom0)
	time.sleep(2)
	block_status1=get_blockStats(dom0)
	block_info=[]
	for block in get_devices(dom0,"devices/disk/source","file"):
		block_info.append(dom0.blockInfo(block,0))
	i=0
	for block in get_devices(dom0,"devices/disk/target","dev"):
		disk_info+=block+'-'+str((block_status1[block][1]-block_status0[block][1])/2048)+'-'+ str((block_status1[block][3]-block_status0[block][3])/2048)+'-'+str(block_info[i][1]/1.0/block_info[i][0]*100)[:5]+'-'+str(block_info[i][0])+'#'
		i=i+1
	return disk_info

def get_domCPUUsage(dom0):
	Pstart_time=time.time()
	Dstart_time=dom0.info()[4]
	time.sleep(2)
	Dstop_time=dom0.info()[4]
	Pstop_time=time.time()
	core_num=int(dom0.info()[3])
	cpu_usage=(Dstart_time-Dstop_time)/(Pstart_time-Pstop_time)/1000000000/core_num*100
	cpu_usage=cpu_usage if (cpu_usage>0) else 0.0
	cpu_usage=cpu_usage if (cpu_usage<100) else 100.0
	return cpu_usage

def get_memory(pid):
	mem=0
	for line in file('/proc/%d/smaps' % int(pid),'r'):
		if re.findall('Private_',line):
			mem+=int(re.findall('(\d+)',line)[0])
	return mem

def get_domMemUsage(dom0):
	pid=(os.popen("ps aux|grep "+dom0.name()+" | grep -v 'grep' | awk '{print $2}'").readlines()[0])
	memstatus=get_memory(pid)
	memusage='%.2f' % (int(memstatus)*100.0/int(dom0.info()[2]))
	return memusage

def get_nicInfo(nics):
	net_status={}
	for nic in nics:
		net_status[nic]=[os.popen("cat /proc/net/dev |grep -w '"+nic+"' |awk '{print $10}'").readlines()[0][:-1],os.popen("cat /proc/net/dev |grep -w '"+nic+"' |awk '{print $2}'").readlines()[0][:-1]]
	return net_status

def get_domNicInfo(dom0):
	net_status0={}
	net_status1={}
	net_info=''
	nics=get_devices(dom0,"devices/interface/target","dev")
	net_status0=get_nicInfo(nics)
	time.sleep(2)
	net_status1=get_nicInfo(nics)
	for nic in nics:
		net_info+=nic+'-'+str((int(net_status1[nic][0])-int(net_status0[nic][0]))/2048)+'-'+str((int(net_status1[nic][1])-int(net_status0[nic][1]))/2048)+'#'
	return net_info

def get_domIPInfo(dom0):
	domMain_info=[]
	#instance_ip=ElementTree.fromstring(dom0.XMLDesc(0)).findall("devices/interface/filterref/parameter")[1].get('value')
	instance_ip = ''
	domMain_info.append(dom0.name())
	domUUID=ElementTree.fromstring(dom0.XMLDesc(0)).findtext('uuid')
	domMain_info.append(domUUID)
	domMain_info.append(instance_ip)
	return domMain_info

def getNodeInfo(domainID):
	conn=libvirt.open("qemu:///system")
	#domainID=76
	if conn==None:
		print "fail to connect hypervisor"
		sys.exit(1)
	try:
		dom0=conn.lookupByID(domainID)
	except:
		print "fail to find the domain"
		sys.exit(1)
	node_info=[]
	node_info.append(get_domCPUUsage(dom0))
	node_info.append(get_domMemUsage(dom0))
	node_info.append(get_domDiskInfo(dom0))
	node_info.append(get_domNicInfo(dom0))
	for info in get_domIPInfo(dom0):
		node_info.append(info)
	return node_info
