#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from models import conn, api
import traceback
from providers.ProviderInterface import ProviderInterface
from pokercms import cmsapi

class CmsProvider(ProviderInterface):
    """
    通用提供商,满足通用api规范则可使用
    """

    conn = None
    authCookie = None

    def __init__(self, conf, dbconf):
        """
        初始化
        """
        self.conn = conn(dbconf)
        apiUser = api.getLoginInfo(self.conn, conf['serviceCode'])
        self.apiUsername = apiUser['username']
        self.apiPwd = apiUser['pw']
        self.apiBack = apiUser['back'] #特殊战局
        self.clubId = '588000'
        self.conf = conf
        self.conn.close()

    def getBuyin(self):
        """
        获取待审批提案列表

        Returns:
            {u'iErrCode': 0, u'result': []}
        """
        return cmsapi.getBuyinList(self.apiUsername, self.apiPwd, self.clubId)

    def acceptBuyin(self, params):
        """
        通过提案

        Args:
            params: 通过的提案信息
                {
                    uuid 用户id string
                    gameRoomId     房间id string
                }
        """

        return cmsapi.acceptBuyin(self.apiUsername,
            self.apiPwd,
            self.clubId,
            params['uuid'],
            params['gameRoomId'])

    def denyBuyin(self, params):
        """
        拒绝提案

        Args:
            params: 拒绝的提案信息
                {
                    uuid 用户id string
                    gameRoomId     房间id string
                }
        """

        return cmsapi.denyBuyin(self.apiUsername,
            self.apiPwd,
            self.clubId,
            params['uuid'],
            params['gameRoomId'])

    def queryUserBoard(self, params):
        """
        查询用户战绩

        Args:
            params: 查询条件
                {
                    pccname : "ABC" 德撲暱稱(string)
                    query_index : 5  起始筆數(int)
                    query_number : 30  回傳筆數(int) 最多30筆
                    query_number : "AAA" 俱樂部名稱(string)
                    end_time_start : "2018-05-06 08:00:23" 牌局結束時間 起始(string)
                    end_time_end : "2018-05-06 08:00:23"   牌局結束時間 結束(string)
                    created_at_start : "2018-05-06 08:00:23" 牌局匯入時間 起始(string)
                    created_at_end : "2018-05-06 08:00:23"   牌局匯入時間 結束(string) 
                }

        Returns:
            待定
        """

        rel = cmsapi.getHistoryGameList(self.apiUsername,
            self.apiPwd,
            self.clubId,
            params['starttime'],
            params['endtime'])

        for key, item in rel['result']['list']:
            # get detail
            detail = cmsapi.getHistoryGameDetail(self.apiUsername, self.apiPwd, self.clubId, item['roomid'])
            rel['result']['list'][key]['detail'] = detail