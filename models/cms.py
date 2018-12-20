#!/bin/python 
# -*- coding: UTF-8 -*-

import time
import datetime
import base64
import traceback
import hashlib

def addBuyinLog(conn, purseInfo, buyin, action):
	with conn.cursor() as cursor:
		clubName = "Not_recorded"
		clubRoomName = base64.b64encode((buyin['club_name']+'_'+buyin['room_name']).encode('utf-8'))
		sql = "INSERT INTO `onethink_cms_buyin_log` ( `userid`, `username`, `game_vid`, `club_id`,"\
		" `join_cash`, `application_time`, `check_time`, `check_user`, `check_status`, `room_name`, `room_id`) "\
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
			buyin['room_id']))

def updatePurse(conn, info, delta, roomId):

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
		        `settle_game_info`
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
		    roomId,
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
		    roomId,
		    info['settle_game_info'],
		  )
		)
	except Exception as e:
		raise e

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
		sql = "INSERT INTO `onethink_cms_buyin_log` ( `userid`, `username`, `game_vid`, `club_id`,"\
		" `join_cash`, `application_time`, `check_time`, `check_user`, `check_status`, `room_name`, `room_id`) "\
		"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(sql,
			(purseInfo['frontend_user_id'],
			purseInfo['frontend_user_auth'],
			purseInfo['game_vid'],
			clubName,
			buyin['buyStack'],
			str(time.time()),
			str(time.time()),
			'Auto_Buyin_Tool_B', 
			'accept',
			buyin['gameRoomName'],
			buyin['gameRoomId']))

		timestamp = str(time.time())
		cash = int(purseInfo['cash'])+int(delta)
		sql = "update onethink_player_purse set cash=%s where id=%s"
		cursor.execute(sql, (str(cash), purseInfo['pp.id']))
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
		        `settle_game_info`
		      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		      """

		print(sql)
		print buyin, identify
		cursor.execute(
		  sql,
		  (
		    purseInfo['frontend_user_auth'],
		    purseInfo['cash'],
		    purseInfo['diamond'],
		    purseInfo['point'],
		    str(cash),
		    purseInfo['diamond'],
		    purseInfo['point'],
		    timestamp,
		    timestamp,
		    buyin['gameRoomId'],
		    identify,
		  )
		)
		cursor.close()
		conn.commit()
	except Exception as e:
		traceback.print_exc()
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


def saveGameinfo(conn, params):
  sql = """
          insert into onethink_historygamelist (
            `roomname`,
            `bigblind`,
            `createuser`,
            `gameroomtype`,
            `hands`,
            `iAnte`,
            `leagueid`,
            `maxplayer`,
            `players`,
            `roomid`,
            `smallblind`,
            `createtime`
          )
          values (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
          )
        """
  cursor = conn.cursor()
  cursor.execute(
    sql,
    (
      params['roomname'],
      str(params['bigblind']),
      params['createuser'],
      str(params['gameroomtype']),
      str(params['hands']),
      str(params['iAnte']),
      str(params['leagueid']),
      str(params['maxplayer']),
      str(params['players']),
      str(params['roomid']),
      str(params['smallblind']),
      str(params['createtime']/1000)
    )
  )

def getCountOfGameinfo(conn, params):
  sql = """
        select count(1) as game_count
        from onethink_historygamelist
        where roomid = %s and createtime = %s
        """

  # print((sql, params))
  with conn.cursor() as cursor:
    cursor.execute(
      sql,
      (
        params['roomid'],
        params['createtime'] / 1000
      )
    )
    return cursor.fetchone()

def saveGameUserRecord(conn, params):
  sql = """
        INSERT INTO `onethink_historygamedetail` (
          `insuranceGetStacks`, 
          `info_id`, 
          `showId`, 
          `clubId`, 
          `bonus`, 
          `strCover`, 
          `strNick`, 
          `strSmallCover`, 
          `gameType`, 
          `clubName`, 
          `buyinStack`, 
          `fantseynum`, 
          `insuranceBuyStacks`, 
          `remainStack`, 
          `uuid`, 
          `insurance`, 
          `InsurancePremium`, 
          `endTime`, 
          `bz_username`, 
          `afbonus`, 
          `back`
        ) 
        VALUES (
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s
        )
        """

  cursor = conn.cursor()
  cursor.execute(
    sql,
    (
      str(params['insuranceGetStacks']),
      params['roomid'],
      params['showId'],
      str(params['clubId']),
      str(params['bonus']),
      params['strCover'],
      params['strNick'],
      params['strSmallCover'],
      params['gameType'],
      params['clubName'],
      str(params['buyinStack']),
      str(params['fantseynum']),
      str(params['insuranceBuyStacks']),
      str(params['remainStack']),
      str(params['uuid']),
      str(params['insurance']),
      str(params['InsurancePremium']),
      str(time.mktime(datetime.datetime.strptime(params['endTime'], "%Y-%m-%d %H:%M:%S").timetuple())),
      str(params['username']),
      str(params['afbonus']),
      str(params['back'])
    )
  )

def getCountOfUser(conn, params):
  sql = """
        select count(1) as user_settle_count
        from onethink_historygamedetail
        where showId = %s and info_id = %s
        """
  with conn.cursor() as cursor:
    cursor.execute(
      sql,
      (
        params['showId'],
        params['roomid']
      )
    )
    return cursor.fetchone()

def getTotoalCmsBuyinAmount(conn, pccid, roomid, beginTime, endTime):
  with conn.cursor() as cursor:
    sql = """
      select
        sum(join_cash) as total_amount
      from
        onethink_cms_buyin_log
      where
        check_time between %s and %s
        and
        game_vid = %s
        and
        room_id = %s
        and
        check_status = 'accept'
    """

    cursor.execute(sql, (beginTime, endTime, pccid, roomid))
    return cursor.fetchone()

def getSpecialRake(conn, cloubId):
  sql = """
        SELECT * 
        FROM `onethink_cms_special_session_back` 
        WHERE `clubid` = %s
        """
  with conn.cursor() as cursor:
    cursor.execute(sql, cloubId)
    return cursor.fetchone()

def addSettleFailLog(conn, params):
	cursor = conn.cursor()
	sql = """
      insert into onethink_cms_game_end(
        game_uid,
        game_name,
        game_id,
        create_game_time,
        end_game_time,
        apply_time,
        action
      )
      values(%s, %s,  %s, %s, %s, %s, %s)
	    """
	cursor.execute(
	    sql,
	    (
	      params['game_uid'],
	      params['game_name'],
	      params['game_id'],
	      params['create_game_time'],
	      params['end_game_time'],
	      params['apply_time'],
	      params['action']
		)
	)
  