#-*- coding: utf-8 -*-

import MySQLdb
import datetime

class DBManager : 
	__dbconn__ = None

	def __init__(self, username, userpw, dbname):
		self.__dbname__ = dbname
		self.__username__ = username
		self.__userpw__ = username

		if DBManager.__dbconn__ == None:
			DBManager.__dbconn__ = MySQLdb.connect('localhost', self.__username__, self.__userpw__, self.__dbname__, charset='utf8', use_unicode=True)
		
		self.cursor = DBManager.__dbconn__.cursor()
		self.cursor.execute('set names utf8')


	def sqlexec(self, sql):
		try:
			self.cursor = DBManager.__dbconn__.cursor()
			
			self.cursor.execute('set names utf8')
			self.cursor.execute(sql.encode('utf-8'))

			if (sql[0:5].lower() != 'select'):
				DBManager.__dbconn__.commit()
			return self.cursor
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			print(sql)
			print(e)


	def fetchone(self):
		return self.cursor.fetchone()
		
	def getconn(self):
		return DBManager.__dbconn__
		
	def getcursor(self):
		return self.cursor

	def close(self):
		if DBManager.__dbconn__ != None:
			DBManager.__dbconn__.close()


class OnejavDB :

	
	def __init__(self):
		self.dbname = 'pupa'
		self.username = 'jykim'
		self.userpw = 'jykim'
		self.dbm = DBManager(self.username, self.userpw, self.dbname)



	def get_kor_name(self, jname):
		sql = u'SELECT kname FROM jav_actress where jname = \'{0}\''.format(jname)
		self.dbm.sqlexec(sql)
		data = self.dbm.fetchone()
		if(data == None): return None
		if(len(data) <= 0): return None
		return data[0]
		
		
	def insert_jpn_name(self, jname):
		sql = u'INSERT INTO jav_actress (jname) VALUES (\'{0}\')'.format(jname)
		self.dbm.sqlexec(sql)

		
	def insert_name_pair(self, jname, kname):
		sql = u'INSERT INTO jav_actress (jname, kname) VALUES (\'{0}\', \'{1}\')'.format(jname, kname)
		self.dbm.sqlexec(sql)
