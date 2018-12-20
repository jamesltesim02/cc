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
        print list
        for item in list:
            print item
            uid = item['showId']
            if int(uid) == 2525717358:
                purseInfo = purse.getPurseInfoByGameId(self.conn, uid)
                data = {
                    'uuid':item['uuid'], 
                    'gameRoomId':item["gameRoomId"],
                }
                if purseInfo:
                    if int(purseInfo['cash']) >= int(item['amounts']):
                        resp = self.api.acceptBuyin(data)
                        print "审核成功", resp
                        if resp['iErrCode'] == 0:
                            try:
                                cms.syncCmsBuyin(self.conn, purseInfo, item, -int(item['amounts']))
                            except Exception as e:
                                print e
                    else:               
                        resp = self.api.denyBuyin(data)
                        if resp['iErrCode'] == 0:
                            cms.addBuyinLog(self.conn, purseInfo, item, 'deny')
                            self.conn.commit()

        self.conn.close()
        
