#!/bin/python 
# -*- coding: UTF-8 -*-

import time
import datetime

def addBuyinLog(conn, purseInfo, buyin, action):
	with conn.cursor() as cursor:
		clubName = "Not_recorded"
		clubRoomName = base64.b64encode((buyin['club_name']+'_'+buyin['room_name']).encode('utf-8'))
		sql = "INSERT INTO `onethink_cms_buyin_log` ( `userid`, `username`, `game_vid`, `club_id`,"\
		" `join_cash`, `application_time`, `check_time`, `check_user`, `check_status`, `room_name`, `room_id`, `club_room_name`) "\
		"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(sql,
			(purseInfo['frontend_user_id'],
			purseInfo['frontend_user_auth'],
			purseInfo['game_vid'],
			clubName,
			buyin['amounts'],
			str(time.time()),
			str(time.time()),
			'Auto_Buyin_Tool_B', 
			action,
			buyin['room_name'],
			buyin['room_id'],
			clubRoomName))

def updatePurse(conn, info, delta):

	cursor = conn.cursor()
	try:
		timestamp = str(time.time())
		cash = int(info['cash'])+int(delta)
		sql = "update onethink_player_purse set cash=%s where id=%s"
		cursor.execute(sql, (str(cash), info['pp.id']))
		sql = """
		      INSERT INTO `onethink_cms_auto_cash_log` (
		        `username`,
		        `cash`,
		        `diamond`,
		        `point`,
		        `change_cash`,
		        `change_diamond`,
		        `change_point`,
		        `apply_time`,
		        `change_time`,
		        `game_id`,
		        `settle_game_info`,
		      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		      """

		print(sql)
		print((
		    info['frontend_user_auth'],
		    info['cash'],
		    info['diamond'],
		    info['point'],
		    str(cash),
		    info['diamond'],
		    info['point'],
		    timestamp,
		    timestamp,
		    info['game_id'],
		    info['settle_game_info'],
		  ))
		cursor.execute(
		  sql,
		  (
		    info['frontend_user_auth'],
		    info['cash'],
		    info['diamond'],
		    info['point'],
		    str(cash),
		    info['diamond'],
		    info['point'],
		    timestamp,
		    timestamp,
		    info['game_id'],
		    info['settle_game_info'],
		  )
		)
		cursor.close()
		conn.commit()
	except Exception as e:
		cursor.close()
		conn.rollback()

def syncCmsBuyin(conn, purseInfo, buyin, delta):
	
	cursor = conn.cursor()
	try:
		now = time.time()
	    buyinKeys = buyin.keys()
	    buyinKeys.sort()
	    identify = ''
	    for key in buyinKeys:
	    	identify += '%s:%s' %(key, buyin[key])
	    identify = hashlib.md5(identify.encode('utf-8')).hexdigest()
	    sql = "select apply_time from onethink_cms_auto_cash_log where settle_game_info=%s order by apply_time desc"
	    cursor.execute(sql, (identify))
	    rel = cursor.fetchone()
	    print rel
	    if rel != None and int(now)-int(rel['apply_time']) <= 24*60*60:
			cursor.close()
			return

		clubName = "Not_recorded"
		clubRoomName = base64.b64encode((buyin['club_name']+'_'+buyin['room_name']).encode('utf-8'))
		sql = "INSERT INTO `onethink_cms_buyin_log` ( `userid`, `username`, `game_vid`, `club_id`,"\
		" `join_cash`, `application_time`, `check_time`, `check_user`, `check_status`, `room_name`, `room_id`, `club_room_name`) "\
		"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(sql,
			(purseInfo['frontend_user_id'],
			purseInfo['frontend_user_auth'],
			purseInfo['game_vid'],
			clubName,
			buyin['amounts'],
			str(time.time()),
			str(time.time()),
			'Auto_Buyin_Tool_B', 
			action,
			buyin['room_name'],
			buyin['room_id'],
			clubRoomName))

		timestamp = str(time.time())
		cash = int(info['cash'])+int(delta)
		sql = "update onethink_player_purse set cash=%s where id=%s"
		cursor.execute(sql, (str(cash), info['pp.id']))
		sql = """
		      INSERT INTO `onethink_cms_auto_cash_log` (
		        `username`,
		        `cash`,
		        `diamond`,
		        `point`,
		        `change_cash`,
		        `change_diamond`,
		        `change_point`,
		        `apply_time`,
		        `change_time`,
		        `game_id`,
		        `settle_game_info`,
		      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		      """

		print(sql)
		print buyin, identify
		cursor.execute(
		  sql,
		  (
		    info['frontend_user_auth'],
		    info['cash'],
		    info['diamond'],
		    info['point'],
		    str(cash),
		    info['diamond'],
		    info['point'],
		    timestamp,
		    timestamp,
		    info['game_id'],
		    identify,
		  )
		)
		cursor.close()
		conn.commit()
	except Exception as e:
		cursor.close()
		conn.rollback()

def getBuyin(conn, gameId, roomName, roomId):

	starttime = (datetime.date.today()-datetime.timedelta(1)).strftime("%s")
	endtime = (datetime.date.today()+datetime.timedelta(1)).strftime("%s")
	sql = "SELECT * FROM `onethink_cms_buyin_log` WHERE "\
	"`game_vid` = %s AND `room_name` = %s AND room_id= %S "\
	"AND `application_time` BETWEEN %s AND %s AND `check_status` = 'accept'"
	with conn.cursor() as cursor:
		cursor.execute(sql, (gameId, roomName, roomid, starttime, endtime))
		return cursor.fetchone()

def check_game_list(conn, createtime, roomid):
	cursor = conn.cursor()
	timestamp, ms = divmod(createtime, 1000)
	sql = "SELECT * FROM `onethink_cms_game_end` WHERE "\
	"`game_id`= %s AND `create_game_time` = %s"
	cursor.execute(sql,(roomId, createtime))
	return cursor.fetchall()