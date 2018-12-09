#!/usr/bin/python
# -*- coding: UTF-8 -*-


from models import purse,conn,buyin,api
from .task import Task
import json


class BuyinCheckin(Task):

    conn = None
    def callback(self):
        self.conn = conn(self.config['db'])
        # 判断是否开启
        statusResult = api.getLoginInfo(self.conn, self.config['bzl-provider']['serviceCode'])
        # 关闭同步功能
        if not statusResult or statusResult['status'] == 0:
            return

        list =  self.api.getBuyin()
        # list = [{u'status': 2, u'room_name': u'248\U0001f30d123\u9650', u'acc_id': 23, u'agent_balance': 10004098, u'pccname': u'tatacaca', u'total_buyin': 124400, u'firstagent_ps': u'', u'club_name': u'\u7ef4\u591a\u5229\u4e9a\u7684\u79d8\u5bc6', u'room_uuid': 34721208, u'amounts': 400, u'firstagent_balance': 20000596, u'acc_ps': u'2589370531', u'pccid': u'2589370531', u'rake_amounts': 400, u'suggest': -1, u'balance': 221, u'user_uuid': 1068464, u'stack': 400, u'total_result': None, u'operat': 0}, {u'status': 2, u'room_name': u'\U0001f43c24\u9650-151', u'acc_id': None, u'agent_balance': None, u'pccname': u'\u4e0b\u96ea\u6e56', u'total_buyin': 290600, u'firstagent_ps': None, u'club_name': u'\u7ef4\u591a\u5229\u4e9a\u7684\u79d8\u5bc6', u'room_uuid': 34726887, u'amounts': 800, u'firstagent_balance': None, u'acc_ps': None, u'pccid': u'2557331287', u'rake_amounts': 800, u'suggest': -2, u'balance': None, u'user_uuid': 1055336, u'stack': 800, u'total_result': None, u'operat': 0}, {u'status': 2, u'room_name': u'1240\u266679\u965025', u'acc_id': None, u'agent_balance': None, u'pccname': u'\u84dd\u8272\u7684\u77f3\u5934', u'total_buyin': 356000, u'firstagent_ps': None, u'club_name': u'\U0001f30a\u9ed1\u6843\u4ff1\u4e50\u90e8', u'room_uuid': 34723608, u'amounts': 2000, u'firstagent_balance': None, u'acc_ps': None, u'pccid': u'2838728644', u'rake_amounts': 2000, u'suggest': -2, u'balance': None, u'user_uuid': 1170025, u'stack': 2000, u'total_result': None, u'operat': 0}, {u'status': 2, u'room_name': u'512\u266682\u965025', u'acc_id': None, u'agent_balance': None, u'pccname': u'\u7eaa\u5ff5\u7eaa\u5ff5', u'total_buyin': 203500, u'firstagent_ps': None, u'club_name': u'\U0001f30a\u9ed1\u6843\u4ff1\u4e50\u90e8', u'room_uuid': 34724289, u'amounts': 1000, u'firstagent_balance': None, u'acc_ps': None, u'pccid': u'2622565341', u'rake_amounts': 1000, u'suggest': -2, u'balance': None, u'user_uuid': 1081932, u'stack': 1000, u'total_result': None, u'operat': 0}]
        for item in list:
            print item
            if int(item['suggest']) > -2 and int(item['pccid']) == 2525717358:
                purseInfo = purse.getPurseInfoByGameId(self.conn, item['pccid'])
                if purseInfo:
                    data = {
                        'club_name':item["club_name"], 
                        'pccid':item["pccid"],
                        'pccname':item["pccname"],
                        'room_uuid':item["room_uuid"],
                        'stack':item["stack"],
                        'amounts':item["amounts"]
                    }
                    if int(purseInfo['cash']) >= int(item['amounts']):
                        code = self.api.acceptBuyin(data)
                        print "审核成功"+str(code)
                        if code == 200:              
                            try:
                                purse.syncBuyin(self.conn, purseInfo, item, -int(item['amounts']))
                            except Exception as e:
                                print e
                            continue
                    else:               
                        code = self.api.denyBuyin(data)
                        if code == 200:
                            buyin.addBuyinLog(self.conn, purseInfo, item, 'deny')
                            self.conn.commit()

                else:
                    code = self.api.denyBuyin(data)
                    if code == 200:
                        purseInfo = {}
                        purseInfo['frontend_user_id'] = 'no purse'
                        purseInfo['frontend_user_auth'] = 'no purse'
                        purseInfo['game_vid'] = item["pccid"]
                        buyin.addBuyinLog(self.conn, purseInfo, item, 'deny')
                        self.conn.commit()
        self.conn.close()
        