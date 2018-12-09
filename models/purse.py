#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql
import datetime
import time
import traceback
import base64
import hashlib


def getBuyin(conn, gameId, roomName):

  starttime = (datetime.date.today()-datetime.timedelta(1)).strftime("%s")
  endtime = (datetime.date.today()+datetime.timedelta(1)).strftime("%s")
  sql = "SELECT * FROM `onethink_join_game_log` WHERE "\
  "`game_vid` = %s AND `room_name` = %s AND `application_time` BETWEEN %s AND %s AND `check_status` = 'accept'"
  with conn.cursor() as cursor:
    cursor.execute(sql, (gameId, roomName, starttime, endtime))
    return cursor.fetchone()


def getPurseInfoByGameId(conn, gameId):
  with conn.cursor() as cursor:
    sql = "select * from onethink_ucenter_vid_member as uv, onethink_player_purse as pp, onethink_ucenter_member as um"\
    " where uv.game_vid=%s and uv.frontend_user_auth = pp.username and uv.frontend_user_auth = um.username"
    cursor.execute(sql, (gameId))
    return cursor.fetchone()

def getTotoalBuyinAmount(conn, pccid, beginTime, endTime, joinToken):
  with conn.cursor() as cursor:
    sql = """
      select
        sum(join_cash) as totalAmount
      from
        onethink_join_game_log
      where
        check_time between %s and %s
        and
        game_vid = %s
        and
        club_room_name = %s
        and
        check_status = 'accept'
    """

    cursor.execute(sql, (beginTime, endTime, pccid, joinToken))
    return cursor.fetchone()
  return

def getSettleRecord(conn, settleGameInfo):
  with conn.cursor() as cursor:
    sql = "select count(1) as settle_count from onethink_auto_api_cash_log where settle_game_info=%s"
    cursor.execute(sql, (settleGameInfo))
    return cursor.fetchone()

def updatePurse(conn, info, delta):

  cursor = conn.cursor()
  try:
    timestamp = str(time.time())
    cash = int(info['cash'])+int(delta)
    sql = "update onethink_player_purse set cash=%s where id=%s"
    cursor.execute(sql, (str(cash), info['pp.id']))
    sql = """
          INSERT INTO `onethink_auto_api_cash_log` (
            `username`,
            `cash`,
            `diamond`,
            `point`,
            `change_cash`,
            `change_diamond`,
            `change_point`,
            `apply_time`,
            `change_time`,
            `settle_game_info`
          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
          insert into onethink_api_import_game_end(
            game_uid,
            game_id,
            board_id,
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
      data['game_id'],
      data['board_id'],
      data['end_game_time'],
      data['apply_time'],
      data['action']
    )
  )

#同步宝芝林，德扑圈结算信息信息
def syncSettlement(conn, gameId, roomName, delta):   
  info = getUserInfoByGameId(gameId)
  if info:
    buyin = getBuyin(gameId, roomName)
    if buyin:
      try:
        updatePurse(info, delta)
        conn.commit()
        return True
      except Exception as e:
        print e
        conn.rollback()
  return False

#同步买入信息
def syncBuyin(conn, purseInfo, buyin, delta):
  cursor = conn.cursor()
  try:
    #防止24h重复审核
    now = time.time()
    buyinKeys = buyin.keys()
    buyinKeys.sort()
    identify = ''
    for key in buyinKeys:
      identify += '%s:%s' %(key, buyin[key])
    identify = hashlib.md5(identify.encode('utf-8')).hexdigest()
    sql = "select apply_time from onethink_auto_api_cash_log where settle_game_info=%s"
    cursor.execute(sql, (identify))
    rel = cursor.fetchone()
    print rel
    if rel != None and int(now)-int(rel['apply_time']) <= 24*60*60:
      cursor.close()
      return

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
      "accept",
      buyin['room_name'].encode('utf-8'),
      clubRoomName))

    timestamp = str(time.time())
    cash = int(purseInfo['cash'])+int(delta)
    sql = "update onethink_player_purse set cash=%s where id=%s"
    cursor.execute(sql, (str(cash), purseInfo['pp.id']))
    sql = """
          INSERT INTO `onethink_auto_api_cash_log` (
            `username`,
            `cash`,
            `diamond`,
            `point`,
            `change_cash`,
            `change_diamond`,
            `change_point`,
            `apply_time`,
            `change_time`,
            `settle_game_info`
          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          """
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
        identify
      )
    )
    cursor.close()
    conn.commit()
  except Exception as e:
    traceback.print_exc()
    cursor.close()
    conn.rollback()
