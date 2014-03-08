import libvirt
 
conn=libvirt.open("qemu:///system")
names=conn.listDomainsID()
print names
