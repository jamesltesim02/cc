#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql
import datetime
import time
from . import conn

def getBuyin(gameId, roomName):

  starttime = (datetime.date.today()-datetime.timedelta(1)).strftime("%s")
  endtime = (datetime.date.today()+datetime.timedelta(1)).strftime("%s")
  sql = "SELECT * FROM `onethink_join_game_log` WHERE `game_vid` = %s AND `room_name` = %s AND `application_time` BETWEEN %s AND %s AND `check_status` = 'accept'"
  with conn.cursor() as cursor:
    cursor.execute(sql, (gameId, roomName, starttime, endtime))
    return cursor.fetchone()


def getPurseInfoByGameId(gameId):
  with conn.cursor() as cursor:
    sql = "select * from onethink_ucenter_vid_member as uv, onethink_player_purse as pp, onethink_ucenter_member as um where uv.game_vid=%s and uv.frontend_user_auth = pp.username and uv.frontend_user_auth = um.username"
    cursor.execute(sql, (gameId))
    return cursor.fetchone()

def getTotoalBuyinAmount(pccid, beginTime, endTime, joinToken):
  with conn.cursor() as cursor:
    sql = """
      select
        sum(join_cash) as totalAmount
      from
        onethink_join_game_log
      where
        check_time between %d and %d
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

def getSettleRecord(settleGameInfo):
  with conn.cursor() as cursor:
    sql = "select count(1) as settle_count from onethink_auto_api_cash_log where settle_game_info=%s"
    cursor.execute(sql, (settleGameInfo))
    return cursor.fetchone()

def updatePurse(info, delta):
  cursor = conn.cursor()
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

def addSettleFailLog(data):
  # add_purse_change_log
  #onethink_api_import_game_end
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
def syncSettlement(gameId, roomName, delta):   
  info = getUserInfoByGameId(gameId)
  if info:
    buyin = getBuyin(gameId, roomName)
    if buyin:
      try:
        updatePurse(info, delta)
        conn.commit()
        return True
      finally:
        conn.rollback()
  return False

#同步买入信息
def syncBuyin(gameId, buyin, action):
  info = getUserInfoByGameId(gameId)
