#!/usr/bin/python
# -*- coding: utf-8 -*-


import time
from . import conn

def addBuyinLog(purseInfo, buyin, action):
	with conn.cursor() as cursor:
		clubName = "Not_recorded"
		sql = "INSERT INTO `onethink_join_game_log` ( `userid`, `username`, `game_vid`, `club_id`, `join_cash`, `application_time`, `check_time`, `check_user`, `check_status`, `room_name`) "\
		"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(sql,
			(purseInfo['frontend_user_id'],
			purseInfo['frontend_user_auth'],
			purseInfo['game_vid'],
			clubName,
			buyin['amounts'],
			str(time.time()),
			'Auto_Buyin_Tool_B', 
			action,
			buyin['room_name']))
