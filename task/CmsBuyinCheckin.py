#!/usr/bin/python
# -*- coding: UTF-8 -*-


from models import purse,conn,cms,api
from .task import Task
import json


class CmsBuyinCheckin(Task):

    providerName = 'cms-provider'  
    conn = None
    def callback(self):
        self.conn = conn(self.config['db'])
        # 判断是否开启
        statusResult = api.getLoginInfo(self.conn, self.config[self.providerName]['serviceCode'])
        # # 关闭同步功能
        # if not statusResult or statusResult['status'] == 0:
        #     return

        rel =  self.api.getBuyin()
        list = rel['result']
        # list = [{u'totalGames': 8, u'gameRoomName': u'\u53d1\u53d1\u53d1', u'totalProfit': 1485, u'uuid': 774478, u'gameRoomId': 35047501, u'strNick': u'\u4e5f\u8bb8\u4f1a\u53d8', u'poolRate': 0, u'showId': u'1868828686', u'strSmallCover': u'http://upyun.pokermate.net/images/male_head.png', u'buyStack': 200, u'leagueId': 0, u'totalBuyin': 1100, u'totalHands': 10, u'leagueName': u'', u'clubId': 0}]
        for item in list:
            print item
            uid = item['showId']
            if int(uid) > 0:
                purseInfo = purse.getPurseInfoByGameId(self.conn, uid)
                data = {
                    'uuid':item['uuid'], 
                    'gameRoomId':item["gameRoomId"],
                }
                print purseInfo
                if purseInfo:
                    if int(purseInfo['cash']) >= int(item['buyStack']):
                        resp = self.api.acceptBuyin(data)
                        print "审核结果", resp
                        if resp['iErrCode'] == 0:
                            try:
                                cms.syncCmsBuyin(self.conn, purseInfo, item, -int(item['buyStack']))
                            except Exception as e:
                                print e
                    else:               
                        resp = self.api.denyBuyin(data)
                        if resp['iErrCode'] == 0:
                            cms.addBuyinLog(self.conn, purseInfo, item, 'deny')
                            self.conn.commit()

        self.conn.close()
        
