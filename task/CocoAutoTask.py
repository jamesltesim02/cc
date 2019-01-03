#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import traceback
import json
import base64
import time
import datetime
import hashlib

from .task import Task
from models import conn, api, purse, cocomodel

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class CocoAutoTask(Task):
    conn = None
    providerName = 'coco-provider'

    def setApi(self, conf):
        Task.setApi(self, conf)
        self.conf = self.api.conf
        self.tempFile = '%s/settlementtime-%s.txt' % (TEMP_DIR, self.conf['name'])
        self.api.setBuyinCallback(self.buyinCallback)

    def buyinCallback(self, data):
        if not data or len(data) == 0:
            return
        
        # 遍历到俱乐部数据
        for clubRecord in data:
            # 判断当前俱乐部下是否有提案
            if (
                # 当前商户下是否有data
                not clubRecord
                or not clubRecord.has_key('data')
                # 文档: 請依據 iErrCode 來判斷資料是否正確, 0 是正確，其餘都不正確 
                or not clubRecord.has_key('iErrCode')
                or clubRecord['iErrCode'] != 0
                # 是否有买入提案
                or not clubRecord['data'].has_key('result')
                or len(clubRecord['data']['result']) == 0
            ):
                continue

            # 遍历得到提案数据
            for buyinRecord in clubRecord['data']['result']:
                # 判断是否为当前代理需要处理的数据
                if not buyinRecord.has_key('status') or buyinRecord['status'] != 'active':
                    continue
                buyinRecord['clubId'] = clubRecord['clubId']
                buyinRecord['clubName'] = clubRecord['sClubName']

                self.applyBuyin(buyinRecord)
    
    def applyBuyin(self, buyinRecord):
        applyConn = conn(self.config['db'])
        applyCursor = applyConn.cursor()
        try:
            purseInfo = purse.getPurseWithCursor(
                applyCursor,
                buyinRecord['showId']
            )

            if not purseInfo:
                print ('coco:autotask:apply:no id:', buyinRecord)
                return

            # 审批标志
            settle_game_info = ''
            for key in buyinRecord:
                settle_game_info += '%s:%s' % (key, buyinRecord[key])
            settle_game_info = hashlib.md5(settle_game_info.encode('utf-8')).hexdigest()
            
            # 判断是否重复审批
            applyCountReult = cocomodel.getCountApply(applyCursor, settle_game_info)
            if applyCountReult['apply_count'] > 0:
                print ('coco:autotask:apply:already applyed', buyinRecord)
                return

            applyAction = ''
            applyClubRommName = base64.b64encode((
                "%s_%s" % (
                    buyinRecord['clubId'],
                    buyinRecord['gameRoomName']
                )).encode('utf-8')
            )

            if int(purseInfo['cash']) >= int(buyinRecord['buyStack']):
                try:
                    applyResult = self.api.acceptBuyin({
                        'clubId': buyinRecord['clubId'],
                        'dpqId': buyinRecord['showId'],
                        'buyinStack': buyinRecord['buyStack'],
                        'roomId': buyinRecord['gameRoomId'],
                        'player': buyinRecord['strNick'],
                        'clubName': buyinRecord['clubName'],
                        'agentName': '',
                        'roomName': buyinRecord['gameRoomName'],
                        'leagueName': buyinRecord['leagueName'],
                        'data[userUuid]': buyinRecord['uuid'],
                        'data[roomId]': buyinRecord['gameRoomId'],
                    })
                    if applyResult and not applyResult['err']:
                        # 审批成功
                        print ('coco:autotask:apply:apply success:', applyResult)
                        purseInfo['settle_game_info'] = settle_game_info
                        # 更新钱包
                        cocomodel.updatePurse(
                            applyCursor,
                            purseInfo,
                            -int(buyinRecord['buyStack'])
                        )
                        applyAction = 'accept'
                    else:
                        # 审批失败
                        print ('coco:autotask:apply:apply error:', applyResult)
                except Exception as e:
                    print ('coco:autotask:apply:apply exception:', e)
                    traceback.print_exc()
            else:
                # 拒绝
                applyAction = 'deny'

            # 审批提案日志
            cocomodel.addApplyLog(
                applyCursor,
                (
                    purseInfo['frontend_user_id'],
                    purseInfo['frontend_user_auth'],
                    purseInfo['game_vid'],
                    buyinRecord['clubName'],
                    buyinRecord['buyStack'],
                    str(time.time()),
                    str(time.time()),
                    'connor_coco_buyin',
                    applyAction,
                    buyinRecord['gameRoomName'],
                    buyinRecord['gameRoomId']
                )
            )

            applyConn.commit()
        except Exception as e:
            applyConn.rollback()
        finally:
            applyConn.close()

    def callback(self):
        # print ('start...')
        # self.api.
        try:
            self.conn = conn(self.config['db'])
            # 判断是否开启
            statusResult = api.getLoginInfo(self.conn, self.conf['serviceCode'])
            # 关闭同步功能
            if not statusResult or statusResult['status'] == 0:
                print('coco:autotask:stoped', statusResult['status'])
                self.api.stopBuyinWork()
                return

            # 开启带入提案审批任务
            self.api.startBuyinWork()
            self.settlement()
                # print('status = 1')
                # self.memberInfo = statusResult
                # self.cursor = self.conn.cursor()
                # self.settlement()
                # self.cursor.close()
                # self.conn.commit()
        except Exception as e:
            print "rollback"
            traceback.print_exc()
            # self.cursor.close()
            self.conn.rollback()
        finally:
            self.conn.close()

    def settlement(self):
        # try:
        #     # 判断是否开启
        #     statusResult = api.getLoginInfo(self.conn, self.conf['serviceCode'])
        #     # 关闭同步功能
        #     if not statusResult or statusResult['status'] == 0:
        #         return
        # except Exception as e:
        #     traceback.print_exc()
        #     return

        now = datetime.datetime.now()
        nowStr = now.strftime('%Y/%m/%d %H:%M')
        lastTimeStr = False
        if os.path.exists(self.tempFile):
            try:
                tempfileReader = open(self.tempFile, 'r')
                lastTimeStr = json.loads(tempfileReader.read())['lastTime']
                lastTime = datetime.datetime.strptime(lastTimeStr,'%Y/%m/%d %H:%M')
                lastTimeStr = (lastTime + datetime.timedelta(minutes = -60)).strftime('%Y/%m/%d %H:%M')
            except Exception as e:
                traceback.print_exc()
        if not lastTimeStr:
            lastTimeStr = (now + datetime.timedelta(days = -3)).strftime('%Y/%m/%d %H:%M')

        try:
            data = self.queryUserBoardList(
                lastTimeStr,
                nowStr
            )
            print(data)
            if not data or data['err'] != False:
                return

            dataList = data['data']
            # dataList = [{u'endTime': u'2019-01-03 20:20:04', u'clubId': 26048334, u'waterBill': 0, u'bonus': 0, u'roomName': u'2/4\u26a1\ufe0f03211\u9650', u'dpqId': 4994638727, u'createUser': u'\u5730\u4e3b\u5bb6\u6709\u4f59\u7cae', u'dpqNick': u'\u6c23pupu', u'clubName': u'\u98de\u5929\u6d6a', u'finalBill': 0, u'insurancePremium': 0}, {u'endTime': u'2019-01-02 21:01:48', u'clubId': 168888, u'waterBill': 0, u'bonus': 0, u'roomName': u'24\u5f3a\U0001f3c6D204', u'dpqId': 4994638727, u'createUser': u'\u5965\u65af\u5361  \U0001f3c6', u'dpqNick': u'\u6c23pupu', u'clubName': u'\u5927\u5bb6\u5ead', u'finalBill': 0, u'insurancePremium': 0}, {u'endTime': u'2019-01-02 00:24:55', u'clubId': 168888, u'waterBill': 0, u'bonus': 0, u'roomName': u'24\u5f3a\U0001f3c6C204', u'dpqId': 4994638727, u'createUser': u'\u5965\u65af\u5361  \U0001f3c6', u'dpqNick': u'\u6c23pupu', u'clubName': u'\u5927\u5bb6\u5ead', u'finalBill': 0, u'insurancePremium': 0}]
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
        # if record['dpqId'] != '2525717358':
        #     print('user is not 2525717358')
        #     return
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
        memberResult = purse.getPurseWithCursor(cursor, record['dpqId'])
        if not memberResult:
            print(('no user'))
            gameEndLog['action'] = 'no UID'
            cocomodel.addSettleFailLog(cursor, gameEndLog)
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
            self.conn.commit()
        except Exception as e:
            traceback.print_exc()
            cursor.close()
            self.conn.rollback()

    def queryUserBoardList(self, start, end):
        params = {
            'dpqName':'',
            'dpqId':'',
            'memberName':'',
            'agentName':'',
            'headAgentName':'',
            'club':'',
            'gameCreator': '',
            'gameName': '',
            "datetimes": '%s - %s' %(start, end)
        }
        print(('query param:', params))
        data = self.api.queryUserBoard(params)

        return data