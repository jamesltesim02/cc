#!/usr/bin/python
# -*- coding: UTF-8 -*-

import traceback
from models import purse, conn, cms, api
from .task import Task
import json


class CmsBuyinCheckin(Task):

    providerName = 'cms-provider'
    conn = None

    def autoBuyin(self):
        rel = self.api.getBuyin()
        list = rel['result']
        for item in list:
            print ('cms check buyin, will check auto buyin:', item)
            uid = item['showId']
            purseInfo = purse.getPurseInfoByGameId(self.conn, uid)
            data = {
                'uuid': item['uuid'],
                'gameRoomId': item["gameRoomId"],
            }
            print ('cms check buyin, purse info:', purseInfo)
            if purseInfo:
                if int(purseInfo['cash']) >= int(item['buyStack']):
                    resp = self.api.acceptBuyin(data)
                    print ("cms check buyin, accept result:", resp)
                    if resp['iErrCode'] == 0:
                        try:
                            cms.syncCmsBuyin(
                                self.conn,
                                purseInfo,
                                item,
                                -int(item['buyStack'])
                            )
                        except Exception as e:
                            print e
                else:
                    resp = self.api.denyBuyin(data)
                    print ("cms check buyin, deny result:", resp)
                    if resp['iErrCode'] == 0:
                        cms.addBuyinLog(self.conn, purseInfo, item, 'deny')
                        self.conn.commit()
            else:
                print ('cms check buyin, no purse')

    def callback(self):
        try:
            self.conn = conn(self.config['db'])
            # 判断是否开启
            statusResult = api.getLoginInfo(
                self.conn, self.config[self.providerName]['serviceCode'])
            # # 关闭同步功能
            # if not statusResult or statusResult['status'] == 0:
            #     return
            self.autoBuyin()
            self.conn.commit()
        except:
            traceback.print_exc()
            self.conn.rollback()
        finally:
            self.conn.close()
