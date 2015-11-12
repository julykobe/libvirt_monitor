import libvirt
import os,sys,re,time
from xml.etree import ElementTree

def getDevices(dom,path,devs):
	tree=ElementTree.fromstring(dom.XMLDesc(0))
	devices=[]
	for target in tree.findall(path):
		dev=target.get(devs)
		if not dev in devices:
			devices.append(dev)
	return devices

def getBlockStats(dom):
	blockStatus={}
	disks=getDevices(dom,"devices/disk/target","dev")
	for block in disks:
		blockStatus[block]=dom.blockStats(block)
	return blockStatus

def getDomDiskInfo(dom0):
	blockStatus0={}
	blockStatus1={}
	diskInfo=''
	blockStatus0=getBlockStats(dom0)
	time.sleep(2)
	blockStatus1=getBlockStats(dom0)
	blockInfo=[]
	for block in getDevices(dom0,"devices/disk/source","file"):
		blockInfo.append(dom0.blockInfo(block,0))
	i=0
	for block in getDevices(dom0,"devices/disk/target","dev"):
		diskInfo+=block+'-'+str((blockStatus1[block][1]-blockStatus0[block][1])/2048)+'-'+ str((blockStatus1[block][3]-blockStatus0[block][3])/2048)+'-'+str(blockInfo[i][1]/1.0/blockInfo[i][0]*100)[:5]+'-'+str(blockInfo[i][0])+'#'
		i=i+1
	return diskInfo

def getDomCpuUsage(dom0):
	PstartTime=time.time()
	DstartTime=dom0.info()[4]
	time.sleep(2)
	DstopTime=dom0.info()[4]
	PstopTime=time.time()
	coreNum=int(dom0.info()[3])
	cpuUsage=(DstartTime-DstopTime)/(PstartTime-PstopTime)/1000000000/coreNum*100
	cpuUsage=cpuUsage if (cpuUsage>0) else 0.0
	cpuUsage=cpuUsage if (cpuUsage<100) else 100.0
	return cpuUsage

def getMemory(pid):
	mem=0
	for line in file('/proc/%d/smaps' % int(pid),'r'):
		if re.findall('Private_',line):
			mem+=int(re.findall('(\d+)',line)[0])
	return mem

def getDomMemUsage(dom0):
	pid=(os.popen("ps aux|grep "+dom0.name()+" | grep -v 'grep' | awk '{print $2}'").readlines()[0])
	memStatus=getMemory(pid)
	memUsage='%.2f' % (int(memStatus)*100.0/int(dom0.info()[2]))
	return memUsage

def getNicInfo(nics):
	netStatus={}
	for nic in nics:
		netStatus[nic]=[os.popen("cat /proc/net/dev |grep -w '"+nic+"' |awk '{print $10}'").readlines()[0][:-1],os.popen("cat /proc/net/dev |grep -w '"+nic+"' |awk '{print $2}'").readlines()[0][:-1]]
	return netStatus

def getDomNicInfo(dom0):
	netStatus0={}
	netStatus1={}
	netInfo=''
	nics=getDevices(dom0,"devices/interface/target","dev")
	netStatus0=getNicInfo(nics)
	time.sleep(2)
	netStatus1=getNicInfo(nics)
	for nic in nics:
		netInfo+=nic+'-'+str((int(netStatus1[nic][0])-int(netStatus0[nic][0]))/2048)+'-'+str((int(netStatus1[nic][1])-int(netStatus0[nic][1]))/2048)+'#'
	return netInfo

def getDomIpInfo(dom0):
	domMainInfo=[]
	#instanceIp=ElementTree.fromstring(dom0.XMLDesc(0)).findall("devices/interface/filterref/parameter")[1].get('value')
	instanceIp = ''
	domMainInfo.append(dom0.name())
	domUUID=ElementTree.fromstring(dom0.XMLDesc(0)).findtext('uuid')
	domMainInfo.append(domUUID)
	domMainInfo.append(instanceIp)
	return domMainInfo

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
	nodeInfo=[]
	nodeInfo.append(getDomCpuUsage(dom0))
	nodeInfo.append(getDomMemUsage(dom0))
	nodeInfo.append(getDomDiskInfo(dom0))
	nodeInfo.append(getDomNicInfo(dom0))
	for info in getDomIpInfo(dom0):
		nodeInfo.append(info)
	return nodeInfo
