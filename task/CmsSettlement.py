#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import traceback
import json
import base64
import time
import datetime
import xlrd
from .task import Task
from models import conn, api, cms, purse

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class CmsSettlement(Task):
    conn = None
    providerName = 'cms-provider'

    def setApi(self, conf):
        Task.setApi(self, conf)
        self.conf = self.api.conf
        self.cursor = None
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
            self.cursor,
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

        print(('will settle user record:', userRecord, gameInfo))

        currentTime = str(time.time())
        gameEndTime = self.getCustTimestamp(userRecord['endTime'])
        gameEndLog = {
            'game_uid': userRecord['showId'],
            'game_name': gameInfo['roomname'],
            'game_id': gameInfo['roomid'],
            'board_id': '',
            'create_game_time': gameInfo['createtime'],
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
        memberResult = purse.getPurseInfoByGameIdWidthCursor(
            self.cursor,
            userRecord['showId']
        )
        if not memberResult:
            print('no user')
            # 记录用户不存在的日志
            gameEndLog['action'] = 'no UID'
            cms.addSettleFailLog(self.cursor, gameEndLog)
            return

        # 查询结算表中是否已有结算记录.如果已经存在,则抛弃
        settleCountResult = cms.getSettleRecord(self.cursor, settleGameInfo)
        if settleCountResult['settle_count'] > 0:
            print(('already settlemented'))
            return
        
        beginTime = self.getCustTimestamp(userRecord['endTime'], minutes = -720)
        endTime = self.getCustTimestamp(userRecord['endTime'], minutes = 120)
        

        # 查询是否有足够的转入金额
        buyinResult = cms.getTotoalCmsBuyinAmount(
            self.cursor,
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
                cms.addSettleFailLog(self.cursor, gameEndLog)
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
                cms.addSettleFailLog(self.cursor, gameEndLog)
            return

        updateBalance = 0
        afterwater = 0
        rake = 0

        if userRecord['bonus'] > 0:
            rake = float(self.getRake(gameInfo['roomname']))
            # 抽水
            afterwater = int(userRecord['bonus'] * rake)
            updateBalance = afterwater + userRecord['buyinStack']
        else:
            updateBalance = userRecord['remainStack']
            afterwater = userRecord['bonus']

        print(({
            'update balance': updateBalance,
            'afterwater': afterwater,
            'rake': rake
        }))

        # 记录用户战绩日志
        userRecord['roomid'] = gameInfo['roomid']
        userRecord['username'] = memberResult['username']
        userRecord['afbonus'] = updateBalance
        userRecord['back'] = afterwater
        cms.saveGameUserRecord(
            self.cursor,
            userRecord
        )

        # 记录结算日志
        gameEndLog['action'] = 'OK'
        cms.addSettleFailLog(self.cursor, gameEndLog)

        # 更新钱包
        memberResult['settle_game_info'] = settleGameInfo
        cms.updatePurse(
            self.cursor,
            memberResult,
            updateBalance,
            gameInfo['roomid']
        )

    # 针对战局进行结算
    def settleGame(self, gameInfo):
        """
        针对每一个战局进行结算
        """

        # 是否已经结算过此战局
        gameCount = cms.getCountOfGameinfo(
            self.cursor,
            {
                'roomid': gameInfo['roomid'],
                'createtime': gameInfo['createtime']
            }
        )

        if gameCount['game_count'] > 0:
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
            self.cursor,
            gameInfo
        )

    # 一次结算任务
    def settlement(self):
        """
        结算
        """
        now = int(time.time() * 1000)
        lastTime = False

        if os.path.exists(self.tempFile):
            try:
                tempfileReader = open(self.tempFile, 'r')
                lastTime = json.loads(tempfileReader.read())['lastTime']
                lastTime = lastTime - 600000
            except Exception as e:
                traceback.print_exc()
        if not lastTime:
            lastTime = (now - (24*60*60*1000))

        roomReuslt = self.api.getHistoryGameList({
            'starttime': lastTime,
            'endtime': now,
        })

        tempfile = open(self.tempFile, 'w+')
        tempfile.write(json.dumps({ 'lastTime': now }))

        # 没有查到战局
        if (
            not roomReuslt 
            or not roomReuslt.has_key('result') 
            or roomReuslt['result']['total'] == 0
        ):
            print('no record')
            return
        
        for gameInfo in roomReuslt['result']['list']:
            self.settleGame(gameInfo)

    # 转换本地excel文件为需要结算的数据格式
    def toData(self, file):
        urColumnMappings = {
            0: 'gameType',
            9: 'showId',
            10: 'strNick',
            11: 'clubId',
            12: 'clubName',
            13: 'buyinStack',
            14: 'remainStack',
            20: 'bonus',
            21: 'endTime'
        }
        giColumnMappings = {
            1: 'roomname',
            2: 'roomid'
        }
        data = []
        print(('cms:begin transfer local file:', file))
        x1 = xlrd.open_workbook(file)
        sheet1 = x1.sheet_by_index(0)
        if sheet1.nrows <= 2:
            return data
        for rn in range(2, sheet1.nrows):
            rowData = {
                'userRecord': {
                'strCover': '',
                'insuranceGetStacks': 0,
                'strSmallCover': '',
                'fantseynum': 0,
                'insuranceBuyStacks': 0,
                'uuid': '',
                'insurance': 0,
                'InsurancePremium': 0
                },
                'gameInfo': {
                'createtime': ''
                }
            }
            row = sheet1.row(rn)
            for cn2 in range(0, len(row)):
                if urColumnMappings.has_key(cn2):
                    name = urColumnMappings[cn2]
                    rowData['userRecord'][name] = row[cn2].value
                if giColumnMappings.has_key(cn2):
                    name = giColumnMappings[cn2]
                    rowData['gameInfo'][name] = row[cn2].value

            print (rowData)

            rowData['userRecord']['buyinStack'] = int(float(rowData['userRecord']['buyinStack']))
            rowData['userRecord']['remainStack'] = int(float(rowData['userRecord']['remainStack']))
            rowData['userRecord']['bonus'] = int(float(rowData['userRecord']['bonus']))

            data.append(rowData)

        print(('local datas:', data))
        return data

    # 手动汇入文件解析
    def localSettlement(self):
        if not 'localDataPath' in self.conf:
            return
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
                    self.settleUserRecord(data[dnum]['userRecord'], data[dnum]['gameInfo'])
                os.remove(rfile)
            except Exception as e:
                print(('local settlement fail:', rfile))
                faileddir = os.path.join(self.conf['localDataPath'], 'failed')
                if not os.path.exists(faileddir):
                    os.makedirs(faileddir)
                os.rename(rfile, os.path.join(faileddir, files[num]))
                traceback.print_exc()



    # 定时任务函数入口
    def callback(self):
        try:
            self.conn = conn(self.config['db'])
            # 判断是否开启
            statusResult = api.getLoginInfo(self.conn, self.conf['serviceCode'])
            # 关闭同步功能
            if not statusResult or statusResult['status'] == 0:
                print('status = 0')
                return

            self.memberInfo = statusResult
            self.cursor = self.conn.cursor()
            # 手动汇入(从本地excel中结算)
            self.localSettlement()
            # 自动汇入(从接口查询结算)
            self.settlement()
            self.cursor.close()
            self.conn.commit()
        except Exception as e:
            print "rollback"
            traceback.print_exc()
            self.cursor.close()
            self.conn.rollback()
        finally:
            self.conn.close()
