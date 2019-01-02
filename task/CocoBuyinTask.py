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

from models import conn, purse, api, member

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

    print(('开始处理:', record))
    
    # 结算判断标志 pccid_roomName_clubName_buyIn_bringOut_endTime
    settleGameInfo = base64.b64encode(
      ('%s_%s_%s_%s_%s_%s'  % (
        record['pccid'],
        record['room_name'],
        record['club_name'],
        record['buy_in'],
        record['bring_out'],
        record['end_time']
      )).encode('utf-8')
    )

    gameEndLog = {
      'game_uid': record['pccid'],
      'game_id': record['room_name'],
      'board_id': '',
      'end_game_time': gameEndTime,
      'apply_time': currentTime,
      'settle_game_info': settleGameInfo,
    }

    # 判断是否查无此人
    memberResult = purse.getPurseInfoByGameId(self.conn, record['pccid'])
    if not memberResult:
      print(('no user'))
      gameEndLog['action'] = 'no UID'
      purse.addSettleFailLog(self.conn, gameEndLog)
      return


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

  def toData(self, file):
    name2columnMap = {
        0: 'pccname',
        1: 'pccid',
        6: 'username',
        8: 'club_name',
        10: 'room_name',
        12: 'end_time',
        14: 'buy_in',
        15: 'bring_out',
        17: 'afterwater'
    }
    data = []
    print(('begin transfer local file:', file))
    x1 = xlrd.open_workbook(file)
    sheet1 = x1.sheet_by_index(0)
    print(sheet1)
    if sheet1.nrows <= 1:
        return data
    for rn in range(1, sheet1.nrows):
        rowData = {}
        row = sheet1.row(rn)
        for cn2 in range(0, len(row)):
            if name2columnMap.has_key(cn2):
                name = name2columnMap[cn2]
                rowData[name] = row[cn2].value

        rowData['buy_in'] = int(float(rowData['buy_in']))
        rowData['bring_out'] = int(float(rowData['bring_out']))
        rowData['afterwater'] = int(float(rowData['afterwater']))

        data.append(rowData)

    print(('local datas:', data))
    return data

  def localSettlement(self):
    if not os.path.exists(self.conf['localDataPath']):
      return
    files = os.listdir(self.conf['localDataPath'])
    print(('local files:', files))
    if len(files) == 0:
      return 

    for num in range(0, len(files)):
      if files[num] == 'failed':
        continue
      try:
        rfile = os.path.join(self.conf['localDataPath'], files[num])
        data = self.toData(rfile)
        if len(data) == 0:
          continue
        for dnum in range(0, len(data)):
          self.settleRecord(data[dnum])
        os.remove(rfile)
      except Exception as e:
        print(('local settlement fail:', rfile))
        faileddir = os.path.join(self.conf['localDataPath'], 'failed')
        if not os.path.exists(faileddir):
          os.makedirs(faileddir)
        os.rename(rfile, os.path.join(faileddir, files[num]))
        traceback.print_exc()


  def callback(self):
    try:
      self.conn = conn(self.config['db'])
      self.localSettlement()
    except Exception as e:
      traceback.print_exc()
    finally:
      self.conn.close()

    try:
      self.conn = conn(self.config['db'])
      self.settlement()
    except Exception as e:
      traceback.print_exc()
    finally:
      self.conn.close()
