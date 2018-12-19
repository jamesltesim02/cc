#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import traceback
import json
import base64
import time
import datetime
from .task import Task
from models import conn, api, cms, purse

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class CmsSettlement(Task):
  conn = None
  providerName = 'cms-provider'

  def setApi(self, conf):
    Task.setApi(self, conf)
    self.conf = self.api.conf
    self.tempFile = '%s/cmssettlementtime-%s.txt' % (TEMP_DIR, self.conf['name'])
    self.memberInfo = None

  # 时间转时间戳
  def getCustTimestamp(self, timeStr, seconds = 0, minutes = 0):
    t = datetime.datetime.strptime(timeStr,'%Y-%m-%d %H:%M:%S')
    t = t + datetime.timedelta(seconds = seconds, minutes = minutes)
    return str(time.mktime(t.timetuple()))

  # 获取抽水额度
  def getRake(self, roomname):
    specials = cms.getSpecialRake(
      self.conn,
      self.conf['cloubId']
    )
    if specials and len(specials) > 0:
      for spe in specials:
        if spe['special_char'] in roomname:
          return spe['back']
    
    return self.memberInfo['back']

  # 结算用户战绩
  def settleUserRecord(self, userRecord, gameInfo):
    """
    针对战绩的每个用户数据进行结算
    """

    print(('will settle user record:', userRecord))

    currentTime = str(time.time())
    gameEndTime = self.getCustTimestamp(gameInfo['endTime'])
    gameEndLog = {
      'game_uid': userRecord['showId'],
      'game_name': gameInfo['roomname'],
      'game_id': gameInfo['roomid'],
      'board_id': '',
      'end_game_time': gameEndTime,
      'apply_time': currentTime
    }


    # 结算标志 showId_roomid_buyinStack_remainStack
    settleGameInfo = base64.b64encode(
      '%s_%s_%s_%s' %(
        userRecord['showId'],
        gameInfo['roomid'],
        userRecord['buyinStack'],
        userRecord['remainStack']
      )
    )

    # 查询用户是否存在
    memberResult = purse.getPurseInfoByGameId(
      self.conn,
      userRecord['showId']
    )
    if not memberResult:
      print('no user')
      # 记录用户不存在的日志
      gameEndLog['action'] = 'no UID'
      cms.addSettleFailLog(self.conn, gameEndLog)
      return

    # 查询结算表中是否已有结算记录.如果已经存在,则抛弃
    settleCountResult = purse.getSettleRecord(self.conn, settleGameInfo)
    if settleCountResult['settle_count'] > 0:
      print(('already settlemented'))
      return
    
    beginTime = self.getCustTimestamp(userRecord['endTime'], minutes = -720)
    endTime = self.getCustTimestamp(userRecord['endTime'], minutes = 120)
    

    # 查询是否有足够的转入金额
    buyinResult = cms.getTotoalCmsBuyinAmount(
      self.conn,
      userRecord['showId'],
      gameInfo['roomid'],
      beginTime,
      endTime
    )

    print(('total buy in:', buyinResult))

    if buyinResult['total_amount'] < userRecord['buyinStack']:
      if not buyinResult['total_amount'] or buyinResult['total_amount'] == 0:
        print('no apply')
        gameEndLog['action'] = 'no Buyin'
        cms.addSettleFailLog(self.conn, gameEndLog)
      else:
        print((
          'amount not match, local:', 
          buyinResult['total_amount'], 
          ', remote', userRecord['buyinStack']
        ))
        gameEndLog['action'] = (
          'no enough, local buyin: %s, remote buyin: %s' % (
            buyinResult['total_amount'],
            userRecord['buyinStack']
          )
        )
        cms.addSettleFailLog(self.conn, gameEndLog)
      return

    updateBalance = 0
    afterwater = 0

    if userRecord['bonus'] > 0:
      rake = float(self.getRake(gameInfo['roomname']))
      # 抽水
      afterwater = int(userRecord['bonus'] * rake)
      updateBalance = afterwater + userRecord['buyinStack']
    else:
      updateBalance = userRecord['remainStack']
      afterwater = userRecord['bonus']

    # 更新钱包
    memberResult['settle_game_info'] = settleGameInfo
    cms.updatePurse(
      self.conn,
      memberResult,
      updateBalance
    )

    # 记录用户战绩日志
    userRecord['roomid'] = gameInfo['roomid']
    userRecord['username'] = memberResult['username']
    userRecord['afbonus'] = updateBalance
    userRecord['back'] = afterwater
    cms.saveGameUserRecord(
      self.conn,
      userRecord
    )

    # 记录结算日志
    gameEndLog['action'] = 'OK'
    cms.addSettleFailLog(self.conn, gameEndLog)

  # 针对战局进行结算
  def settleGame(self, gameInfo):
    """
    针对每一个战局进行结算
    """

    # 是否已经结算过此战局
    gameCount = cms.getCountOfGameinfo(
      self.conn,
      {
        'roomid': gameInfo['roomid'],
        'createtime': gameInfo['createtime']
      }
    )
    if gameCount['settle_count'] > 0:
      print(('game already settlemented:', gameInfo))
      return
    
    # 查询战绩
    gameDetailResult = self.api.getGameDetail({
      'room_id': gameInfo['roomid']
    })

    if (
      not gameDetailResult
      or not gameDetailResult.has_key('result')
      or len(gameDetailResult['result']) == 0
    ):
      return
    
    for userRecord in gameDetailResult['result']:
      self.settleUserRecord(userRecord, gameInfo)

    # 将战局结算记录插入表中
    cms.saveGameinfo(
      self.conn,
      gameInfo
    )

  # 一次结算任务
  def settlement(self):
    """
    结算
    """
    now = datetime.datetime.now()
    nowStr = now.strftime('%Y-%m-%d %H:%M:%S')
    lastTimeStr = False

    if os.path.exists(self.tempFile):
      try:
        tempfileReader = open(self.tempFile, 'r')
        lastTimeStr = json.loads(tempfileReader.read())['lastTime']
        lastTime = datetime.datetime.strptime(lastTimeStr,'%Y-%m-%d %H:%M:%S')
        lastTimeStr = (lastTime + datetime.timedelta(minutes = -60)).strftime('%Y-%m-%d %H:%M:%S')
      except Exception as e:
        traceback.print_exc()
    if not lastTimeStr:
      lastTimeStr = (now + datetime.timedelta(days = -3)).strftime('%Y-%m-%d %H:%M:%S')

    roomReuslt = self.api.getHistoryGameList({
      'starttime': lastTimeStr,
      'endtime': nowStr,
    })

    # 没有查到战局
    if (
      not roomReuslt 
      or not roomReuslt.has_key('result') 
      or roomReuslt['result']['total'] == 0
    ):
      return
    
    for gameInfo in roomReuslt['result']['list']:
      self.settleGame(gameInfo)

  # 定时任务函数入口
  def callback(self):
    try:
      self.conn = conn(self.config['db'])
      # 判断是否开启
      statusResult = api.getLoginInfo(self.conn, self.conf['serviceCode'])
      # 关闭同步功能
      if not statusResult or statusResult['status'] == 0:
        return
      
      self.memberInfo = statusResult
    except Exception as e:
      traceback.print_exc()
    finally:
      self.conn.close()

    # 结算
    try:
      self.conn = conn(self.config['db'])
      self.settlement()
      self.conn.commit()
    except Exception as e:
      self.conn.rollback()
    finally:
      self.conn.close()