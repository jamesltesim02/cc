#!/usr/bin/python
# -*- coding: UTF-8 -*-

# ALTER TABLE `onethink_auto_api_cash_log`
# 	ADD COLUMN `settle_game_info` VARCHAR(255) NULL AFTER `change_time`;

import os
import json
import requests
import base64
import time
import datetime

from models import purse

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class Settlement:
    def __init__(self, provider):
        self.provider = provider
        self.conf = provider.conf
        self.tempFile = '%s/settlementtime-%s.txt' % (TEMP_DIR, self.conf['name'])

    def queryUserBoardList(self, start, end, index = 0):
        params = {
            "end_time_start": start,
            "end_time_end": end,
            "query_index": index
        }
        data = self.provider.queryUserBoard(params)

        if len(data) >= 30:
            newdata = self.queryUserBoardList(start, end, index = index + 30)
            data.extend(newdata)

        return data

    def settlement(self):
        now = datetime.datetime.now()
        nowStr = now.strftime('%Y-%m-%d %H:%M:%S')
        lastTimeStr = False
        if os.path.exists(self.tempFile):
            try:
                tempfileReader = open(self.tempFile, 'r')
                lastTimeStr = json.loads(tempfileReader.read())['lastTime']
                lastTime = datetime.datetime.strptime(lastTimeStr,'%Y-%m-%d %H:%M:%S')
                lastTimeStr = (lastTime + datetime.timedelta(minutes = -500)).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(e)
        if not lastTimeStr:
            lastTimeStr = (now + datetime.timedelta(days = -3)).strftime('%Y-%m-%d %H:%M:%S')

        dataList = self.queryUserBoardList(
            lastTimeStr,
            nowStr,
            0
        )

        tempfile = open(self.tempFile, 'w+')
        tempfile.write(json.dumps({
            'lastTime': nowStr
        }))

        for record in dataList:
            self.settleRecord(record)

    def getCustTimestamp(self, timeStr, seconds = 0):
        t = datetime.datetime.strptime(timeStr,'%Y-%m-%d %H:%M:%S')
        t = t + datetime.timedelta(seconds = seconds)
        return t

    def settleRecord(self, record):
        # pccid_table_number_boardId_roomId_clubUuid_buyIn_bringOut
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

        # 查询提案表中是有对应提案,如果没有则抛弃
        joinToken = base64.b64encode('%s_%s' % (record['club_name'], record['room_name']))
        beginTime = self.getCustTimestamp(record['created_at'], seconds = -60)
        endTime = self.getCustTimestamp(record['end_time'], seconds = 60)
        buyInAmountResult = purse.getTotoalBuyinAmount(
            beginTime,
            endTime,
            record['created_at'],
            joinToken
        )

        if buyInAmountResult['totalAmount'] < record['buy_in']:
            # 如果大于0 则记录日志并返回
            # 如果为0 直接返回
            return
        
        # 查询反水额度计算反水

        # 更新钱包

        # 记录结算日志

        # commit
        # print(record)


# now = datetime.datetime.now()
# nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
# print(nowstr)

# delta = datetime.timedelta(days=-3)
# n_days = now + delta
# n_daysstr = n_days.strftime('%Y-%m-%d %H:%M:%S')
# print(n_daysstr)