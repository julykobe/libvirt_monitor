#! /usr/bin/env python
import dbHelper
import getNodeInfo
import time
import libvirt

conn=libvirt.open("qemu:///system")
IDs=conn.listDomainsID()

for domainID in IDs:
	node_info=getNodeInfo.getNodeInfo(domainID)
	cmd="insert into vm_instance(cpuUsage,memUsage,diskInfo,netInfo,instance_name,instance_id,instance_ip,timeStamp) Values(%.5f,%f,'%s','%s','%s','%s','%s','%s')" % (node_info[0],float(node_info[1]),node_info[2],node_info[3],node_info[4],node_info[5],node_info[6],str(time.strftime("%Y-%m-%d %X", time.localtime())))
	dbHelper.insertRecord(cmd)
