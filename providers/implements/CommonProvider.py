#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import requests
import base64
from providers.ProviderInterface import ProviderInterface

TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

class CommonProvider(ProviderInterface):
    """
    通用提供商,满足通用api规范则可使用
    """

    def __init__(self, conf):
        """
        初始化
        """

        self.conf = conf
        self.tempFile = '%s/%s.txt' % (TEMP_DIR, self.conf['name'])

    def __login__(self):
        """
        登录
        """

        loginAuth = base64.b64encode('%s:%s' % (self.conf['username'], self.conf['password']))
        loginResult =  requests.post(
            self.conf['loginApi'],
            data = { 'authorization': loginAuth }
        )

        self.authCookie = loginResult.cookies.get_dict()
        tempfile = open(self.tempFile, 'w+')
        tempfile.write(json.dumps(self.authCookie))

    def __invoke__(self, url, method = 'post', params = {}, needAuth = True):
        """
        调用接口
        """

        if needAuth:
            if hasattr(self, 'authCookie') == False:
                if os.path.exists(self.tempFile) == False:
                    self.__login__()
                tempfileReader = open(self.tempFile, 'r')
                self.authCookie = json.loads(tempfileReader.read())

        if method == 'get':
            result = requests.get(url, params = params, cookies = self.authCookie).json()
        else:
            result = requests.post(url, data = params, cookies = self.authCookie).json()

        if result['reponse_data_num'] != 1:
            self.__login__()
            return self.__invoke__(url, method, params, needAuth)

        return result

    def getBuyin(self):
        """
        获取待审批提案列表

        Returns:
            buyinList 提案列表
                [
                    {
                        "status": 0,   状态(等待处理 已处理)
                        "acc_id": 14632, 玩家编号
                        "agent_balance": 119916, 代理余额(不需要理会)
                        "pccname": "\u6d9bs", "total_buyin": 38600, 德扑暱称 
                        "room_uuid": 31944804,  房间编号
                        "club_name": "\ud83c\udf0a\u9ed1\u6843\u4ff1\u4e50\u90e8",  俱乐部名称
                        "room_name": "248\u266668\u965025",  房间名称(牌局名)
                        "stack": 800,    
                        "amounts": 800, 要求买入金额
                        "firstagent_balance": 119916, 总代理余额(不需要理会)
                        "acc_ps": null,  会员注解(不需要理会)
                        "pccid": "2639477333", 会员德扑ID
                        "rake_amounts": 800,   加权后的买入金额(不需要理会)
                        "suggest": 0, 建议(可买入 不可买入)(不需要理会)
                        "balance": 50524, 余额 (不需要理会)
                        "user_uuid": 1088802, (不需要理会)
                        "firstagent_ps": "",  (不需要理会)
                        "total_result": null, (不需要理会)
                        "operat": 1           (不需要理会)
                    }
                ]
        """

        return self.__invoke__(
            self.conf['buyinApi'],
            method = 'get'
        )['data']

    def acceptBuyin(self, params):
        """
        通过提案

        Args:
            params: 通过的提案信息
                {
                    club_name 俱乐部名称 string
                    pccid     俱乐部ID string
                    pccname   玩家德扑暱称 string
                    room_uuid 房间编号 string
                    amounts   买入金额 int 由/api/club_buyin
                }
        """

        return self.__invoke__(
            self.conf['acceptApi'],
            params
        )

    def denyBuyin(self, params):
        """
        拒绝提案

        Args:
            params: 拒绝的提案信息
                {
                    club_name 俱乐部名称 string
                    pccid     俱乐部ID string
                    pccname   玩家德扑暱称 string
                    room_uuid 房间编号 string
                    amounts   买入金额 int 由/api/club_buyin
                }
        """

        return self.__invoke__(
            self.conf['denyApi'],
            params
        )

    def getHistoryGameDetails(self, params):
        """
        查询战绩

        Args:
            params: 过滤时间条件
                {
                    startdate 开始时间
                    enddate   结束时间
                }
        """

        return self.__invoke__(
            self.conf['gameDetailsApi'],
            params
        )