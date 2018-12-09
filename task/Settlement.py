#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import requests
import base64
import time
import datetime
from .task import Task

import traceback

from models import conn, purse, api, member

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class Settlement(Task):
  
  conn = None

  def setApi(self, conf):
    Task.setApi(self, conf)
    self.conf = self.api.conf
    self.tempFile = '%s/settlementtime-%s.txt' % (TEMP_DIR, self.conf['name'])

  def queryUserBoardList(self, start, end, index = 0):
    params = {
      "end_time_start": start,
      "end_time_end": end,
      "query_index": index
    }
    print(('query param:', params))
    data = self.api.queryUserBoard(params)

    if len(data) >= 30:
      newdata = self.queryUserBoardList(start, end, index = index + 30)
      data.extend(newdata)

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
      dataList = self.queryUserBoardList(
        lastTimeStr,
        nowStr,
        0
      )

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
    if record['pccid'] != '2525717358':
      print('user is not 2525717358')
      return
    currentTime = str(time.time())
    gameEndTime = self.getCustTimestamp(record['end_time'])

    gameEndLog = {
      'game_uid': record['pccid'],
      'game_id': record['room_name'],
      'board_id': record['board_id'],
      'end_game_time': gameEndTime,
      'apply_time': currentTime
    }


    print(('开始处理:', record))

    # 判断是否查无此人
    memberResult = purse.getPurseInfoByGameId(self.conn, record['pccid'])
    if not memberResult:
      print(('no user'))
      gameEndLog['action'] = 'no UID'
      purse.addSettleFailLog(self.conn, gameEndLog)
      return

    # 结算判断的标志 pccid_table_number_boardId_roomId_clubUuid_buyIn_bringOut
    settleGameInfo = base64.b64encode(
      '%s_%s_%s_%s_%s_%s_%s'  % (
        record['pccid'],
        record['table_number'],
        record['board_id'],
        record['room_id'],
        record['club_uuid'],
        record['buy_in'],
        record['bring_out'],
      )
    )

    # 查询结算表中是否已有结算记录.如果已经存在,则抛弃
    countResult = purse.getSettleRecord(self.conn, settleGameInfo)
    if countResult['settle_count'] > 0:
      print(('already settlemented'))
      return

    # 查询游戏期间该用户的所有带入金额是否足够与代理接口一致,不足则不结算
    joinToken = base64.b64encode(('%s_%s' % (record['club_name'], record['room_name'])).encode('utf-8'))
    print(('join token is:', joinToken))

    beginTime = self.getCustTimestamp(record['end_time'], minutes = -720)
    endTime = self.getCustTimestamp(record['end_time'], minutes = 120)
    buyInAmountResult = purse.getTotoalBuyinAmount(
      self.conn,
      record['pccid'],
      beginTime,
      endTime,
      joinToken
    )

    print(('total buy in:',buyInAmountResult))

    if buyInAmountResult['totalAmount'] < record['buy_in']:
      if not buyInAmountResult['totalAmount'] or buyInAmountResult['totalAmount'] == 0:
        print(('no apply'))
        gameEndLog['action'] = 'no Buyin'
      else:
        print(('amount not match, local:', buyInAmountResult['totalAmount'], ', remote', record['buy_in']))
        gameEndLog['action'] = 'no enough, local buyin: %s, remote buyin: %s' % (buyInAmountResult['totalAmount'], record['buy_in'])
    
      purse.addSettleFailLog(self.conn, gameEndLog)
      return

    # 记录结算日志
    gameEndLog['action'] = 'OK'
    purse.addSettleFailLog(self.conn, gameEndLog)

    memberResult['settle_game_info'] = settleGameInfo

    # 更新钱包
    purse.updatePurse(self.conn, memberResult, record['buy_in'] + record['afterwater'])

  def callback(self):
    try:
      self.conn = conn(self.config['db'])
      self.settlement()
    except Exception as e:
      traceback.print_exc()
    finally:
      self.conn.close()
