import MySQLdb
import dbConf

def getConnection(key=None):
	try:
		conn=MySQLdb.connect(host=dbConf.DBHOST,user=dbConf.DBUSER,passwd=dbConf.DBPASSWORD,db=dbConf.DB)
		return conn
	except:
		print "fail to connect database"
		return None
def insertRecord(cmd):
	result=1
	conn=getConnection()
	if conn==None:
		result=0
	else:
		try:
			cursor=conn.cursor()
			cursor.execute(cmd)
			conn.commit()
		except StandardError as err:
			print str(err)
			conn.rollback()
			result=0
		finally:
			conn.close()	
	return result	


