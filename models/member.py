#!/usr/bin/python
# -*- coding: utf-8 -*-


from cron.models import conn

def getMemberInfo(gameId):
	with conn.cursor() as cursor:
		sql = "SELECT * FROM `onethink_ucenter_vid_member` as a , `onethink_ucenter_member` as b "\
		"WHERE `game_vid` = %s AND a.`frontend_user_auth` = b.username"
		cursor.execute(sql, gameId)
		return cursor.fetchone()
