#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 接口提供商接口, 用于规范提供商函数
# 不同的供应商应有具体实现
# 不允许直接使用提供商接口对象使用
# 也不应直接创建provider对象使用
# 应使用ProviderFactory中的createProvider创建provider对象使用
class ProviderInterface:

    def __init__(self):
        raise Exception('不允许直接对ProviderInterface创建对象,请使用具体提供商实现类')

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

        raise Exception('getBuyin必须在实现类中重写实现')

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

        raise Exception('acceptBuyin必须在实现类中重写实现')

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

        raise Exception('denyBuyin必须在实现类中重写实现')

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

        raise Exception('queryUserBoard必须在实现类中重写实现')