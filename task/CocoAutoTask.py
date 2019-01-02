#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import traceback
import json
import base64
import time
import datetime

from .task import Task
from models import conn, api

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class CocoAutoTask(Task):
    conn = None
    providerName = 'coco-provider'

    def setApi(self, conf):
        Task.setApi(self, conf)
        self.conf = self.api.conf
        self.tempFile = '%s/settlementtime-%s.txt' % (TEMP_DIR, self.conf['name'])
        self.api.setBuyinCallback(self.buyinCallback)

        # time.sleep(20)
        # self.api.stopBuyinWork()

        # time.sleep(10)
        # self.api.startBuyinWork()

    def buyinCallback(self, data):
        print ('buyin data:', data)

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
