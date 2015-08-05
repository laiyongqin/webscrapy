# -*- coding: utf-8 -*-

import MySQLdb

print '<?xml version="1.0" encoding="UTF-8"?>'
print '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
print '<plist version="1.0">'
print '<array>'

try:
	conn = MySQLdb.connect(host="192.168.58.212", user="root", passwd="lm123", db="comm", charset="utf8")
	cur = conn.cursor()
	cur.execute("SELECT * FROM REFERENCE WHERE REF_TYPE = 'Province'")
	for row in cur.fetchall():
		provinceCode = row[2]
		provinceName = row[3]
		
		print '<dict>'	
		print '<key>Province</key>'
		print '<string>' + provinceName + '</string>'
		print '<key>Code</key>'
		print '<string>' + str(provinceCode) + '</string>'
		print '<array>'
		
		sql2 = "SELECT r.REF_CODE, r.DESCRIPTION FROM REFERENCE r, REFERENCE_FILTER f WHERE r.REF_CODE = f.REF_CODE AND f.REF_FILTER_CODE = '" + str(provinceCode) + "'"
		cur.execute(sql2)
		for row in cur.fetchall():
			cityCode = row[0]
			cityName = row[1]
			
			print '<dict>'	
			print '<key>City</key>'
			print '<string>' + cityName + '</string>'
			print '<key>Code</key>'
			print '<string>' + str(cityCode) + '</string>'
			print '<array>'
			
			sql3 = "SELECT r.REF_CODE, r.DESCRIPTION FROM REFERENCE r, REFERENCE_FILTER f WHERE r.REF_CODE = f.REF_CODE AND f.REF_FILTER_CODE = '" + str(cityCode) + "'"
			cur.execute(sql3)
			for row in cur.fetchall():
				countyCode = row[0]
				countyName = row[1]
				
				print '<dict>'
				print '<key>County</key>'
				print '<string>' + countyName + '</string>'
				print '<key>Code</key>'
				print '<string>' + str(countyCode) + '</string>'
				print '</dict>'
				
			print '</array>'
			print '</dict>'
		
		print '</array>'
		print '</dict>'
	cur.close()
	conn.close()
except MySQLdb.Error, e:
	print "Mysql Error %d : %s" % (e.args[0], e.args[1])