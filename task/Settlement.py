#!/usr/bin/python
# -*- coding: UTF-8 -*-

# ALTER TABLE `onethink_auto_api_cash_log`
# 	ADD COLUMN `settle_game_info` VARCHAR(255) NULL AFTER `change_time`;

# ALTER TABLE `onethink_api_import_game_end`
# 	CHANGE COLUMN `game_id` `game_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'API遊戲局ID' AFTER `game_uid`,
# 	ADD COLUMN `board_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'api游戏局id' AFTER `game_id`;

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
        data = self.api.queryUserBoard(params)

        if len(data) >= 30:
            newdata = self.queryUserBoardList(start, end, index = index + 30)
            data.extend(newdata)

        return data

    def settlement(self):
        # try:
        #     # 判断是否开启
        #     statusResult = api.getLoginInfo(5)
        #     # 关闭同步功能
        #     if not statusResult or statusResult['status'] == 0:
        #         return
        # except Exception as e:
        #     print(e)
        #     return
        
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
                print(e)
        if not lastTimeStr:
            lastTimeStr = (now + datetime.timedelta(days = -3)).strftime('%Y-%m-%d %H:%M:%S')

        try:
            dataList = self.queryUserBoardList(
                lastTimeStr,
                nowStr,
                0
            )

            for record in dataList:
                self.settleRecord(record)

            tempfile = open(self.tempFile, 'w+')
            tempfile.write(json.dumps({
                'lastTime': nowStr
            }))
        except Exception as e:
            print(e)

    def getCustTimestamp(self, timeStr, seconds = 0):
        t = datetime.datetime.strptime(timeStr,'%Y-%m-%d %H:%M:%S')
        t = t + datetime.timedelta(seconds = seconds)
        return str(time.mktime(t.timetuple()))

    def settleRecord(self, record):
        currentTime = str(time.time())
        gameEndTime = self.getCustTimestamp(record['end_time'])

        gameEndLog = {
            'game_uid': record['pccid'],
            'game_id': '',
            'board_id': record['board_id'],
            'end_game_time': gameEndTime,
            'apply_time': currentTime
        }

        # 判断是否查无此人
        memberResult = member.getMemberInfo(record['pccid'])
        if not memberResult:
            gameEndLog['action'] = 'no UID'
            purse.addSettleFailLog(gameEndLog)
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
        countResult = purse.getSettleRecord(settleGameInfo)
        if countResult['settle_count'] > 0:
            return

        # 查询游戏期间该用户的所有带入金额是否足够与代理接口一致,不足则不结算
        joinToken = base64.b64encode(('%s_%s' % (record['club_name'], record['room_name'])).encode('utf-8'))
        beginTime = self.getCustTimestamp(record['created_at'], seconds = -60)
        endTime = self.getCustTimestamp(record['end_time'], seconds = 60)
        buyInAmountResult = purse.getTotoalBuyinAmount(
            beginTime,
            endTime,
            record['created_at'],
            joinToken
        )
        if buyInAmountResult['totalAmount'] < record['buy_in']:
            if buyInAmountResult['totalAmount'] == 0:
                gameEndLog['action'] = 'no Buyin'
            else:
                gameEndLog['action'] = 'no enough, local buyin: %s, remote buyin: %s' % (buyInAmountResult['totalAmount'], record['buy_in'])
            
            purse.addSettleFailLog(gameEndLog)
            return

        # 记录结算日志
        gameEndLog['action'] = 'OK'
        purse.addSettleFailLog(gameEndLog)

        # 更新钱包
        purse.updatePurse(memberResult, record['buy_in'] + record['afterwater'])

    def callback(self):
        try:
            self.settlement()
            conn.commit()
        except Exception as e:
            conn.rollback()
            traceback.print_exc()