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
			buyin['room_id']
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
        info['game_id']
        info['settle_game_info']
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
        info['game_id']
        info['settle_game_info']
      )
    )
    cursor.close()
    conn.commit()
  except Exception as e:
    cursor.close()
    conn.rollback()


def addSettleFailLog(conn, data):
  	cursor = conn.cursor()
  	sql = """
          insert into onethink_cms_game_end(
            game_uid,
            game_name,
            game_id,
            board_id,
            create_game_time,
            end_game_time,
            apply_time,
            action
          )
          values(%s, %s,  %s, %s, %s, %s)
        """
	cursor.execute(
	    sql,
	    (
	      data['game_uid'],
	      data['game_name'],
	      data['game_id'],
	      data['board_id'],
	      data['create_game_time']
	      data['end_game_time'],
	      data['apply_time'],
	      data['action']
		)
	)


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