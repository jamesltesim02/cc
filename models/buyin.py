#!/usr/bin/python
# -*- coding: utf-8 -*-


import time
import base64
from . import conn

def addBuyinLog(purseInfo, buyin, action):
	with conn.cursor() as cursor:
		clubName = "Not_recorded"
		clubRoomName = base64.b64encode((buyin['club_name']+'_'+buyin['room_name']).encode('utf-8'))
		sql = "INSERT INTO `onethink_join_game_log` ( `userid`, `username`, `game_vid`, `club_id`,"\
		" `join_cash`, `application_time`, `check_time`, `check_user`, `check_status`, `room_name`, `club_room_name`) "\
		"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
			clubRoomName))
