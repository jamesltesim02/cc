#!/usr/bin/python
# -*- coding: utf-8 -*-

API_BZL_ID = 3

def getLimitGameId():
	with conn.cursor() as cursor:
		sql = "SELECT `game_id` FROM `onethink_api_import_game_end` ORDER BY id desc LIMIT 1"
		cursor.execute(sql)
		rel = cursor.fetchone()
		return rel['game_id']


def get_login_info(apiId):
	with conn.cursor() as cursor:
		sql = "SELECT * FROM `onethink_api_member` WHERE `id` = %s"
		cursor.execute(sql, apiId)
		rel = cursor.fetchone()
		return rel