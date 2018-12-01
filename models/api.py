#!/usr/bin/python
# -*- coding: utf-8 -*-


from cron.models import conn

API_BZL_ID = 3

def getLimitGameId():
	with conn.cursor() as cursor:
		sql = "SELECT `game_id` FROM `onethink_api_import_game_end` ORDER BY id desc LIMIT 1"
		cursor.execute(sql)
		rel = cursor.fetchone()
		return rel['game_id']


def getLoginInfo(apiId):
	with conn.cursor() as cursor:
		sql = "SELECT * FROM `onethink_api_member` WHERE `id` = %s"
		cursor.execute(sql, apiId)
		rel = cursor.fetchone()
		return rel

def insertGameList(gameInfo):
	cursor = conn.cursor()
	timestamp, ms = divmod(game_list_info['createtime'], 1000)
	sql = "INSERT INTO `onethink_historygamelist`(`roomname`, `bigblind`, `createuser`, `gameroomtype`, `hands`, `iAnte`, `leagueid`, `maxplayer`, `players`, `roomid`, `smallblind`, `createtime`)"\
	" VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
	cursor.execute(sql,
		gameInfo['roomname'],
		gameInfo['bigblind'],
		gameInfo['createuser'],
		str(gameInfo['gameroomtype']),
		str(gameInfo['hands']),
		str(gameInfo['iAnte']),
		str(gameInfo['leagueid']),
		str(gameInfo['maxplayer']),
		str(gameInfo['players']),
		str(gameInfo['roomid']),
		str(gameInfo['smallblind']),
		str(gameInfo['timestamp']))

def insertGameDetail(gameDetail, info_id, username, bonus, back):
	cursor = conn.cursor()
	insert_sql = "INSERT INTO `onethink_historygamedetail`(`insuranceGetStacks`, `info_id`, `showId`, `clubId`, `bonus`, `strCover`, `strNick`, `strSmallCover`, `gameType`, `clubName`, `buyinStack`, `fantseynum`, `insuranceBuyStacks`, `remainStack`, `uuid`, `insurance`, `InsurancePremium`, `endTime`, `bz_username`, `afbonus`, `back`) "\
	"VALUES ('"+ str(game_detail['insuranceGetStacks'])+"','"+ info_id +"','"+ game_detail['showId']+"','"+ str(game_detail['clubId'])+"','"+ str(game_detail['bonus'])+"','"+ game_detail['strCover']+"','"+ game_detail['strNick']+"','"+ game_detail['strSmallCover']+"','"+ game_detail['gameType']+"','"+ game_detail['clubName']+"','"+ str(game_detail['buyinStack'])+"','"+ str(game_detail['fantseynum'])+"','"+ str(game_detail['insuranceBuyStacks'])+"','"+ str(game_detail['remainStack'])+"','"+ str(game_detail['uuid'])+"','"+ str(game_detail['insurance'])+"','"+ str(game_detail['InsurancePremium'])+"','"+ str(time.mktime(datetime.datetime.strptime(game_detail['endTime'], "%Y-%m-%d %H:%M:%S").timetuple()))+"','"+ str(username)+"','"+ str(bonus)+"','"+ str(back)+"');"
	cursor.execute(sql,
		gameInfo['roomname'],
		gameInfo['bigblind'],
		gameInfo['createuser'],
		str(gameInfo['gameroomtype']),
		str(gameInfo['hands']),
		str(gameInfo['iAnte']),
		str(gameInfo['leagueid']),
		str(gameInfo['maxplayer']),
		str(gameInfo['players']),
		str(gameInfo['roomid']),
		str(gameInfo['smallblind']),
		str(gameInfo['timestamp']))

def getSpecialBack(clubid):
	cursor = conn.cursor()
	sql = "SELECT * FROM `onethink_cms_special_session_back` WHERE `clubid` = %s"
	cursor.execute(sql, clubid)
	return cursor.fetchone()


def addApiImportLog(uid, roomname, roomid, createtime, enddate, action, applyTime):

	enddate = str(time.mktime(datetime.datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple()))
	timestamp, ms = divmod(createtime, 1000)
	cursor = conn.cursor()
	sql = "INSERT INTO `onethink_cms_game_end`(`game_uid`, `game_name`, `game_id`, `create_game_time`, `end_game_time`, `apply_time`, `action`) "\
	"VALUES (%s, %s, %s, %s, %s, %s, %s);"
	cursor.execute(sql,
		uid,
		roomname,
		str(roomid),
		str(timestamp),
		str(enddate),
		applyTime,
		action)
