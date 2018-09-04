import pymysql
import yaml

with open("config/config.yml", "r") as ymlfile:
	cfg = yaml.load(ymlfile)

def connect_db():
	data = pymysql.connect(cfg["mysql"]["host"], cfg["mysql"]["user"], cfg["mysql"]["pass"], cfg["mysql"]["db"])
	return data

async def save_all_servers(client):
	db = connect_db()
	with db.cursor() as cursor:
		for serv in client.servers:
			Sname = serv.name
			Sid = serv.id

			"""check the server isn't already here"""
			qry = "SELECT `servername`, `serverid` FROM `servers` WHERE `serverid` LIKE \'" + Sid + "\';"
			cursor.execute(qry)
			result = cursor.fetchall()
			"""If no server found with this ID we should add that now."""
			if len(result) < 1:
				qry = "INSERT INTO `servers` (`uid`, `servername`, `serverid`) VALUES (NULL, '%s', '%s')"
				cursor.execute(qry, Sname, Sid)
				db.commit()

async def save_server(id, name):
	db = connect_db()
	with db.cursor() as cursor:
		qry = "SELECT `servername`, `serverid` FROM `servers` WHERE `serverid` LIKE \'" + id + "\';"
		cursor.execute(qry)
		if len(cursor.fetchall()) > 0:
			qry = "INSERT INTO `servers` (`uid`, `servername`, `serverid`) VALUES (NULL, '{0}', '{1}')".format(name, id)
			cursor.execute(qry)
			db.commit()
			return 1
		else:
			return 0

def load_admins():
	db = pymysql.connect(cfg["mysql"]["host"], cfg["mysql"]["user"], cfg["mysql"]["pass"], cfg["mysql"]["db"])
	admins = []
	with db.cursor() as cursor:
		qry = "SELECT `discordid` FROM `users`"
		cursor.execute(qry)
		result = cursor.fetchall()
		for person in result:
			admins.append(person[0])
		return admins

async def db_add_admin(id, name, suffix, serverid):
	db = connect_db()
	with db.cursor() as cursor:
		qry = "SELECT `discordid` FROM `users` WHERE `discordid` LIKE \'" + id + "\';"
		cursor.execute(qry)
		result = cursor.fetchall()
		if result:
			return 0
		else:
			qry = "INSERT INTO `users` (`discordid`, `name`, `serverid`, `suffix`, `is_admin`) VALUES ('{0}', '{1}', '{2}', '{3}', '1')".format(id, name, serverid, suffix)
			cursor.execute(qry)
			db.commit()
			return 1

async def db_del_admin(id):
	db = connect_db()
	with db.cursor() as cursor:
		qry = "SELECT `discordid` FROM `users` WHERE `discordid` LIKE \'" + id + "\';"
		cursor.execute(qry)
		result = cursor.fetchall()
		if result:
			qry = "DELETE FROM `users` WHERE `users`.`discordid` = '{0}'".format(id)
			cursor.execute(qry)
			db.commit()
			return 1
		else:
			return 0
