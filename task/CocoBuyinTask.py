#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import base64
import time
import datetime
import xlrd
from .task import Task

import traceback

from models import conn, purse, api, member, cocomodel

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class Settlement(Task):
  
  conn = None
  providerName = 'coco-provider'

  def setApi(self, conf):
    Task.setApi(self, conf)
    self.conf = self.api.conf
    self.tempFile = '%s/settlementtime-%s.txt' % (TEMP_DIR, self.conf['name'])

  def queryUserBoardList(self, start, end):
    params = {
      "datetimes": '%s - %s' %(start, end)
    }
    print(('query param:', params))
    data = self.api.queryUserBoard(params)

    return data

  def settlement(self):
    try:
      # 判断是否开启
      statusResult = api.getLoginInfo(self.conn, self.conf['serviceCode'])
      # 关闭同步功能
      if not statusResult or statusResult['status'] == 0:
        return
    except Exception as e:
      traceback.print_exc()
      return
    
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

    try:
      data = self.queryUserBoardList(
        lastTimeStr,
        nowStr
      )
      if not data or data['err'] != False:
        return

      dataList = data['data']
      print(dataList)

      if dataList:
        print(('fetch:', len(dataList)))

        for record in dataList:
          self.settleRecord(record)
      else:
        print(('no records'))

      tempfile = open(self.tempFile, 'w+')
      tempfile.write(json.dumps({ 'lastTime': nowStr }))
    except Exception as e:
      traceback.print_exc()

  def getCustTimestamp(self, timeStr, seconds = 0, minutes = 0):
    t = datetime.datetime.strptime(timeStr,'%Y-%m-%d %H:%M:%S')
    t = t + datetime.timedelta(seconds = seconds, minutes = minutes)
    return str(time.mktime(t.timetuple()))

  def settleRecord(self, record):
    if record['dpqId'] != '2525717358':
      print('user is not 2525717358')
      return
    currentTime = str(time.time())
    gameEndTime = self.getCustTimestamp(record['endTime'])

    print(('开始处理:', record))
    
    # 结算判断标志
    settleGameInfo = base64.b64encode(
      ('%s_%s_%s_%s_%s_%s_%s'  % (
        record['dpqId'],
        record['clubId'],
        record['createUser'],
        record['roomName'],
        record['endTime'],
        record['bonus'],
        record['waterBill']
      )).encode('utf-8')
    )

    gameEndLog = {
      'game_uid': record['dpqId'],
      'game_id': record['roomName'],
      'board_id': '',
      'end_game_time': gameEndTime,
      'apply_time': currentTime,
      'settle_game_info': settleGameInfo,
    }

    cursor = self.conn.cursor()

    # 判断是否查无此人
    memberResult = purse.getPurseInfoByGameId(self.conn, record['dpqId'])
    if not memberResult:
      print(('no user'))
      gameEndLog['action'] = 'no UID'
      purse.addSettleFailLog(self.conn, gameEndLog)
      return


    try:
        # 查询结算表中是否已有结算记录.如果已经存在,则抛弃
        countResult = cocomodel.getSettleRecord(cursor, settleGameInfo)
        if countResult['settle_count'] > 0:
          print(('already settlemented'))
          return

        # 查询游戏期间该用户的所有带入金额是否足够与代理接口一致,不足则不结算
        joinToken = base64.b64encode(('%s_%s' % (record['clubId'], record['roomName'])).encode('utf-8'))
        print(('join token is:', joinToken))

        beginTime = self.getCustTimestamp(record['endTime'], minutes = -720)
        endTime = self.getCustTimestamp(record['endTime'], minutes = 120)
        buyInAmountResult = cocomodel.getTotoalBuyinAmount(
          cursor,
          record['dpqId'],
          beginTime,
          endTime,
          joinToken
        )

        print(('total buy in:',buyInAmountResult))

        if not buyInAmountResult['totalAmount'] or buyInAmountResult['totalAmount'] == 0:
            print(('no apply'))
            gameEndLog['action'] = 'no Buyin'
        
            cocomodel.addSettleFailLog(cursor, gameEndLog)
            return

        # 记录结算日志
        gameEndLog['action'] = 'OK'
        cocomodel.addSettleFailLog(cursor, gameEndLog)

        memberResult['settle_game_info'] = settleGameInfo

        # 更新钱包
        cocomodel.updatePurse(cursor, memberResult, buyInAmountResult['totalAmount'] + record['bonus'])
        cocomodel.updateBuyinLog(
          cursor,
          record['dpqId'],
          beginTime,
          endTime,
          joinToken)
        cursor.close()
        self.commit()
    except Exception as e:
        traceback.print_exc()
        cursor.close()
        self.rollback()

  def callback(self):
    try:
      self.conn = conn(self.config['db'])
      self.settlement()
    except Exception as e:
      traceback.print_exc()
    finally:
      self.conn.close()
