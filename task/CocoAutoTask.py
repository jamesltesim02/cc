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
        """
        买入提案审批回调
        """

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
                or not clubRecord['data'].has_key('iErrCode')
                or clubRecord['data']['iErrCode'] != 0
                # 是否有买入提案
                or not clubRecord['data'].has_key('result')
                or len(clubRecord['data']['result']) == 0
            ):
                print ('coco:autotask:apply:no data:', clubRecord)
                continue

            # 遍历得到提案数据
            for buyinRecord in clubRecord['data']['result']:
                # 判断是否为当前代理需要处理的数据
                if not buyinRecord.has_key('status') or buyinRecord['status'] != 'active':
                    print ('coco:autotask:apply:not need apply:', buyinRecord)
                    continue

                buyinRecord['clubId'] = clubRecord['clubId']
                buyinRecord['clubName'] = clubRecord['sClubName']
                self.applyBuyin(buyinRecord)
    
    def applyBuyin(self, buyinRecord):
        """
        买入提案逐条审批
        """

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

            reqData = {
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
            }

            if int(purseInfo['cash']) >= int(buyinRecord['buyStack']):
                print ('coco:autotask:apply:apply accept:', reqData)
                try:
                    applyResult = self.api.acceptBuyin(reqData)
                    if applyResult and not applyResult['err']:
                        # 审批成功
                        print ('coco:autotask:apply:apply success:', applyResult)
                        purseInfo['settle_game_info'] = settle_game_info
                        # 更新钱包
                        cocomodel.applyUpdatePurse(
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
                print ('coco:autotask:apply:apply deny:', reqData)
                applyResult = self.api.denyBuyin(reqData)
                # 拒绝
                applyAction = 'deny'

            # 审批提案日志
            cocomodel.addApplyLog(
                applyCursor,
                (
                    str(purseInfo['frontend_user_id']),
                    str(purseInfo['frontend_user_auth']),
                    str(purseInfo['game_vid']),
                    buyinRecord['clubName'].encode('utf-8'),
                    str(buyinRecord['buyStack']),
                    str(time.time()),
                    str(time.time()),
                    'connor_coco_buyin',
                    str(applyAction),
                    buyinRecord['gameRoomName'].encode('utf-8'),
                    str(applyClubRommName)
                )
            )

            applyConn.commit()
        except Exception as e:
            applyConn.rollback()
            print ('coco:autotask:apply:exception:', e)
            traceback.print_exc()
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
