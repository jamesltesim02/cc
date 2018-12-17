#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime

API_BZL_ID = 3


def getLimitGameId(conn):
    with conn.cursor() as cursor:
        sql = "SELECT `game_id` FROM `onethink_api_import_game_end` ORDER BY id desc LIMIT 1"
        cursor.execute(sql)
        rel = cursor.fetchone()
        return rel['game_id']


def getLoginInfo(conn, apiId):
    with conn.cursor() as cursor:
        sql = "SELECT * FROM `onethink_api_member` WHERE `id` = %s"
        cursor.execute(sql, (apiId))
        rel = cursor.fetchone()
        return rel


def insertGameList(conn, gameInfo):
    cursor = conn.cursor()
    timestamp, ms = divmod(game_list_info['createtime'], 1000)
    sql = "INSERT INTO `onethink_historygamelist`(`roomname`, `bigblind`, `createuser`, `gameroomtype`, `hands`, `iAnte`, `leagueid`, `maxplayer`, `players`, `roomid`, `smallblind`, `createtime`)"\
        " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(
		sql,
        (
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
			str(gameInfo['timestamp'])
		)
	)


def insertGameDetail(conn, gameDetail, infoId, username, bonus, back):
    cursor = conn.cursor()
    sql = "INSERT INTO `onethink_historygamedetail`(`insuranceGetStacks`, `info_id`, `showId`, `clubId`, `bonus`, `strCover`, `strNick`, `strSmallCover`, `gameType`, `clubName`, `buyinStack`, `fantseynum`, `insuranceBuyStacks`, `remainStack`, `uuid`, `insurance`, `InsurancePremium`, `endTime`, `bz_username`, `afbonus`, `back`) "\
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(
		sql,
        (
			gameDetail['insuranceGetStacks'],
			infoId,
			gameDetail['showId'],
			str(gameDetail['clubId']),
			str(gameDetail['bonus']),
			str(gameDetail['strCover']),
			str(gameDetail['gameType']),
			str(gameDetail['clubName']),
			str(gameDetail['buyinStack']),
			str(gameDetail['remainStack']),
			str(gameDetail['uuid']),
			str(gameDetail['insurance']),
			str(gameDetail['InsurancePremium']),
			str(time.mktime(datetime.datetime.strptime(game_detail['endTime'], "%Y-%m-%d %H:%M:%S").timetuple())),
			username,
			str(bonus),
			str(back)
		)
	)


def getGameList(conn, createtime, roomid):
    cursor = conn.cursor()
    timestamp, ms = divmod(createtime, 1000)
    sql = "SELECT * FROM `onethink_historygamelist` WHERE `roomid` = %s AND `createtime` = %s"
    cursor.execute(sql, (str(roomid), str(timestamp)))
    return cursor.fetchone()


def check_game_detail(conn, roomid, uid):
    cursor = conn.cursor()
    sql = "SELECT * FROM `onethink_historygamedetail` WHERE `showId` = %s AND `info_id` = %s"
    cursor.execute(sql, (str(uid), str(roomid)))
    return cursor.fetchone()


def getSpecialBack(conn, clubid):
    cursor = conn.cursor()
    sql = "SELECT * FROM `onethink_cms_special_session_back` WHERE `clubid` = %s"
    cursor.execute(sql, (clubid))
    return cursor.fetchone()


def addApiImportLog(conn, uid, roomname, roomid, createtime, enddate, action, applyTime):

    enddate = str(time.mktime(datetime.datetime.strptime(
        enddate, "%Y-%m-%d %H:%M:%S").timetuple()))
    timestamp, ms = divmod(createtime, 1000)
    cursor = conn.cursor()
    sql = "INSERT INTO `onethink_cms_game_end`(`game_uid`, `game_name`, `game_id`, `create_game_time`, `end_game_time`, `apply_time`, `action`) "\
        "VALUES (%s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(
		sql,
		(
			uid,
			roomname,
			str(roomid),
			str(timestamp),
			str(enddate),
			applyTime,
			action
		)
	)


def updateChingApiStatus(conn, column, status):
    sql = """
        update onethink_ching_realtime_status
        set
            %s='%s'
		where
			id = 1
        """ % (column, status)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        conn.rollback()
