#!/usr/bin/python
# -*- coding: utf-8 -*-


def getMemberInfo(conn, gameId):
	with conn.cursor() as cursor:
		sql = "SELECT * FROM `onethink_ucenter_vid_member` as a , `onethink_ucenter_member` as b "\
		"WHERE `game_vid` = %s AND a.`frontend_user_auth` = b.username"
		cursor.execute(sql, (gameId))
		return cursor.fetchone()

def getUserCount(conn, pccid):
	with conn.cursor() as cursor:
		sql = """
			SELECT 
				count(1) as member_count
			FROM 
				`onethink_ucenter_vid_member` AS a, 
				`onethink_player_purse` AS b,
				`onethink_ucenter_member` AS c

			WHERE
				a.frontend_user_auth = b.username 
				AND 
				a.frontend_user_auth = c.username
				AND
				a.game_vid = %s
			"""
		cursor.execute(sql, (pccid))
		return cursor.fetchone()