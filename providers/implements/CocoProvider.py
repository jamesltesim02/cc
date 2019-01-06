#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import requests
import base64
from models import conn, api
import traceback
import threading
import logging
import time
from socketIO_client_nexus import SocketIO, BaseNamespace, LoggingNamespace
from providers.ProviderInterface import ProviderInterface

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

# logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
# logging.basicConfig()

class CocoBuyinNamespace(BaseNamespace):
    def on_connect(self):
        print ('coco:buyinworker:namespace:connected')
    def on_disconnect(self):
        print ('coco:buyinworker:namespace:disconnected')
    def on_reconnect(self):
        print ('coco:buyinworker:namespace:reconnected')

class CocoBuyinWorker:
    buyinCallback = None
    url = None
    socketIO = None
    provider = None
    buyinNamespace = None
    thread = None
    working = False
    clientTag = ''

    def __init__(self, url, provider):
        self.url = url
        self.provider = provider
        self.thread = threading.Thread(target=self.__wait__)
        self.thread.start()

    def setBuyinCallback(self, buyinCallback):
        self.buyinCallback = buyinCallback
        self.__regCallback__()

    def __wait__(self):
        print('coco:buyinworker:will wait')
        while True:
            if not self.working or not self.socketIO:
                time.sleep(5)
            else:
                try:
                    self.socketIO.wait(5)
                except Exception as e:
                    print ('coco:buyinworker:waiting error:', e)
                    traceback.print_exc()

    def __regCallback__(self):
        if self.buyinNamespace and self.buyinCallback:
            self.buyinNamespace.on(self.clientTag, self.buyinCallback)

    def __success__(self, clientId):
        print ('coco:buyinworker:success:client id:', clientId)
        self.clientTag = 'client:%s' % clientId
        self.__regCallback__()

    def __onConnect__(self):
        print ('coco:buyinworker:connected')

    def __onDisconnect__(self):
        print ('coco:buyinworker:disconnected')

    def __onReconnect__(self):
        print ('coco:buyinworker:reconnected')

    def start(self, cookie):
        if self.working:
            return
        print('coco:buyinworker:will start:', cookie)
        try:
            self.socketIO = SocketIO(
                self.url,
                cookies = cookie,
            )
            self.socketIO.on('connect', self.__onConnect__)
            self.socketIO.on('disconnect', self.__onDisconnect__)
            self.socketIO.on('reconnect', self.__onReconnect__)

            self.buyinNamespace = self.socketIO.define(CocoBuyinNamespace, '/cms')
            self.buyinNamespace.on('success', self.__success__)
            self.buyinNamespace.emit('authentication')
            self.working = True
        except Exception as e:
            print ('coco:buyinworker:connetion error:', e)
            traceback.print_exc()
            self.working = False
            self.buyinNamespace = None
            self.socketIO = None
            self.start(self.provider.getCookie())

    def stop(self):
        if not self.working:
            return
        if self.buyinNamespace:
            self.buyinNamespace.off(self.clientTag)
        if self.socketIO:
            self.socketIO.disconnect()

        self.working = False
        self.buyinNamespace = None
        self.socketIO = None
        self.clientTag = None
        print ('coco:buyinworker:stoped')

class CocoProvider(ProviderInterface):
    conn = None
    authCookie = None
    buyinWoker = None

    def __init__(self, conf, dbconf):
        """
        初始化
        """

        self.dbconf = dbconf
        self.conf = conf
        self.tempFile = '%s/%s.txt' % (TEMP_DIR, self.conf['name'])
        self.buyinWorker = CocoBuyinWorker(conf['wsUrl'], self)

    def getCookie(self):
        self.__login__()
        return  self.authCookie

    def __login__(self):
        try:
            self.conn = conn(self.dbconf)
            statusResult = api.getLoginInfo(self.conn, self.conf['serviceCode'])
        except Exception as e:
            traceback.print_exc()
            return
        finally:
            self.conn.close()
        
        try:
            loginResponse =  requests.post(
                '%s/auth/login' % self.conf['apiUrl'],
                data = {
                    'username': statusResult['username'],
                    'password': statusResult['pw']
                }
            )

            loginResult = loginResponse.json()

            if 'errCode' in loginResult:
                if loginResult['errCode'] == 0:
                    self.authCookie = loginResponse.cookies.get_dict()
                    tempfile = open(self.tempFile, 'w+')
                    tempfile.write(json.dumps(self.authCookie))
                    print ('coco:login:success:', loginResponse)
                if loginResult['errCode'] == 1:
                    print ('coco:login:password error:', loginResponse)
                if loginResult['errCode'] == 2:
                    print ('coco:login:server result error:', loginResponse)
            else:
                print ('coco:login:server result error:no errCode:', loginResponse)

        except Exception as e:
            print ('coco:login:fail:', e)
            traceback.print_exc()

    def setBuyinCallback(self, buyinCallback):
        """
        设置买入提案回调
        """
        self.buyinWorker.setBuyinCallback(buyinCallback)

    def startBuyinWork(self):
        if not self.authCookie:
            self.__login__()
        self.buyinWorker.start(self.authCookie)

    def stopBuyinWork(self):
        self.buyinWorker.stop()

    def __invoke__(self, url, method = 'post', params = {}, needAuth = True):
        """
        调用接口
        """
        if needAuth:
            if hasattr(self, 'authCookie') == False:
                if os.path.exists(self.tempFile) == False:
                    self.__login__()
                else:
                    try:
                        tempfileReader = open(self.tempFile, 'r')
                        self.authCookie = json.loads(tempfileReader.read())
                    except Exception as e:
                        print(e)
                    if not self.authCookie:
                        self.__login__()
        reqUrl = '%s/%s' % (self.conf['apiUrl'], url)
        # print ('coco:invoke:will invoke:', reqUrl, params)
        i = 0
        while i < 3:
            try:
                
                if method == 'get':
                    resultResponse = requests.get(reqUrl, params = params, cookies = self.authCookie)
                else:
                    resultResponse = requests.post(reqUrl, data = params, cookies = self.authCookie)

                # 如果不是json,则证明登录失效
                if resultResponse.headers['Content-Type'] != 'application/json; charset=utf-8':
                    print ('coco:invoke:need login:', reqUrl, params, self.authCookie)
                    self.__login__()
                    i+=1
                    continue

                return resultResponse.json()
            except Exception as e:
                print ('coco:invoke:error', e)
                traceback.print_exc()

        print ('coco:invoke:error 3 times.')

        return None

    def acceptBuyin(self, params):
        """
        通过提案

        Args:
            params: 通过的提案信息
            {
                clubId   俱樂部 ID
                dpqId  玩家德撲圈 ID 
                buyinStack 玩家買入
                roomId 遊戲局 ID
                player 玩家暱稱
                clubName 俱樂部名稱
                roomName 遊戲局名
                agentName 代理名稱
                leagueName: 聯盟名
                data[userUuid]: 玩家 uuid
                data[roomId]: 遊戲局 ID 
            }
        """

        return self.__invoke__('home/game/verify/acceptBuyin', params = params)

    def denyBuyin(self, params):
        """
        拒绝提案

        Args:
            params: 拒绝的提案信息
            {
                clubId   俱樂部 ID
                dpqId  玩家德撲圈 ID 
                buyinStack 玩家買入
                roomId 遊戲局 ID
                player 玩家暱稱
                clubName 俱樂部名稱
                roomName 遊戲局名
                agentName 代理名稱
                leagueName: 聯盟名
                data[userUuid]: 玩家 uuid
                data[roomId]: 遊戲局 ID 
            }
        """

        return self.__invoke__('home/game/verify/denyBuyin', params = params)

    def queryUserBoard(self, params):
        """
        查询用户战绩
        Args:
            params: 查询条件
                {
                    dpqName:
                    dpqId:
                    memberName:
                    agentName:
                    headAgentName:
                    club:
                    gameCreator:
                    gameName:
                    datetimes: 2018/12/19 18:56 - 2018/12/20 18:56 
                } 

                必填欄位:
                    datetimes 為時間範圍，範圍不可超過 60 天，格式請依照 'YYYY/MM/DD HH:mm' 

                其它欄位為選填
                    dpqId 為遊戲帳號，填入後可以查詢該遊戲帳號戰績 

                Ex:
                dpqName=&dpqId=&memberName=&agentName=&headAgentName=&club=&gameCreator=&gameName=&datetimes=2018%2F12%2F19+18%3A56++2018%2F12%2F20+18%3A56
                列出 2018/12/19 18:56 - 2018/12/20 18:56 這一天之內的戰績 
        Returns:
            待定
        """

        return self.__invoke__('home/game/history/search', params = params)
