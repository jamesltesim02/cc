#!/usr/bin/python
# -*- coding: utf-8 -*-


import pymysql
import datetime
import time


conn = pymysql.connect(host='54.213.203.214',
                       port=3306,
                       user='test',
                       password='10-9=1',
                       db='holdem',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)

def getBuyin(gameId, roomName):

  starttime = (datetime.date.today()-datetime.timedelta(1)).strftime("%s")
  endtime = (datetime.date.today()+datetime.timedelta(1)).strftime("%s")
  sql = "SELECT * FROM `onethink_join_game_log` WHERE `game_vid` = %s AND `room_name` = %s AND `application_time` BETWEEN %s AND %s AND `check_status` = 'accept'"
  with cursor.cursor() as cursor:
    cursor.execute(sql, uid, roomName, starttime, endtime)
    return cursor.fetchone(sql)


def getUserInfoByGameId(gameId):
  with conn.cursor() as cursor:
    sql = "select * from onethink_ucenter_vid_member as uv, onethink_player_purse as pp, onethink_ucenter_member as um where uv.game_vid=%s and uv.frontend_user_auth = pp.username and uv.frontend_user_auth = um.username"
    cursor.execute(sql, gameId)
    return cursor.fetchone()

def updatePurse(info, delta):
  cursor = conn.cursor()
  timestamp = str(time.time())
  cash = int(info['cash'])+int(delta)
  sql = "update onethink_player_purse set cash=%s where id=%s"
  cursor.execute(sql, str(cash), info['pp.id'])
  sql = "INSERT INTO `onethink_auto_api_cash_log` (`username`, `cash`, `diamond`, `point`, `change_cash`, `change_diamond`, `change_point`, `apply_time`, `change_time`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
  cursor.execute(sql,
    info['frontend_user_auth'],
    info['cash'],
    info['diamond'],
    info['point'],
    str(cash),
    info['diamond'],
    info['point'],
    timestamp,
    timestamp)

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

string = "ddd" \
"ddd"
print string

