#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from models import conn, api
import traceback
from providers.ProviderInterface import ProviderInterface

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
        apiUser = api.getLoginInfo(self.conn, conf['seviceCode'])
        self.apiUsername = apiUser['username']
        self.apiPwd = apiUser['pw']
        self.apiBack = apiuser['back'] #特殊战局
        self.clubId = '21647880'
        self.conf = conf
        self.tempFile = '%s/%s.txt' % (TEMP_DIR, self.conf['name'])

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
        return cms.getBuyinList(self.apiUsername, self.apiPwd, self.clubId)

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

        return cms.acceptBuyin(self.apiUsername,
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
                    club_name 俱乐部名称 string
                    pccid     俱乐部ID string
                    pccname   玩家德扑暱称 string
                    room_uuid 房间编号 string
                    amounts   买入金额 int 由/api/club_buyin
                }
        """

        return cms.denyBuyin(self.apiUsername,
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

        return cms.getHistoryGameList(self.apiUsername,
            self.apiPwd,
            self.clubId,
            params['starttime'],
            params['endtime'])
